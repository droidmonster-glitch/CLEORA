import os
os.environ.setdefault("DATABASE_URL","sqlite:///test-cleora.db")
os.environ.setdefault("AREZKI_TOKEN","test-arezki-token-0000000000")
os.environ.setdefault("SARAH_TOKEN","test-sarah-token-00000000000")
from uuid import uuid4
from datetime import date,timedelta
from fastapi.testclient import TestClient
from main import app,engine,Base,tokens
import pytest

@pytest.fixture
def client():
    Base.metadata.drop_all(engine)
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(engine)

def headers(owner="arezki"): return {"Authorization":"Bearer "+tokens[owner]}
def event():
    return {"event_id":str(uuid4()),"kind":"created","reservation_id":str(uuid4()),
            "property_id":"arezki-0","arrival":str(date.today()+timedelta(days=40)),
            "departure":str(date.today()+timedelta(days=42))}

def test_tenant_isolation(client):
    assert client.get("/workspace").status_code in (401,403)
    assert client.get("/workspace",headers={"Authorization":"Bearer bad"}).status_code==401
    a=client.get("/workspace",headers=headers()).json()
    b=client.get("/workspace",headers=headers("sarah")).json()
    assert {p["id"] for p in a["properties"]}.isdisjoint(p["id"] for p in b["properties"])
    assert client.post("/simulate",headers=headers("sarah"),json=event()).status_code==404
    assert client.post("/bookings/arezki-b0/question",headers=headers("sarah"),json={"text":"parking"}).status_code==404

def test_lifecycle_and_idempotency(client):
    e=event()
    assert client.post("/simulate",headers=headers(),json=e).json()["applied"]
    assert not client.post("/simulate",headers=headers(),json=e).json()["applied"]
    d=client.get("/workspace",headers=headers()).json()
    assert len(d["notifications"])==2
    assert len(d["reminders"])==1
    bad={**e,"guest":"Autre"} 
    assert client.post("/simulate",headers=headers(),json=bad).status_code==409
    updated={**e,"event_id":str(uuid4()),"kind":"updated","departure":str(date.today()+timedelta(days=43))}
    assert client.post("/simulate",headers=headers(),json=updated).status_code==200
    cancelled={**updated,"event_id":str(uuid4()),"kind":"cancelled"}
    assert client.post("/simulate",headers=headers(),json=cancelled).status_code==200
    d=client.get("/workspace",headers=headers()).json()
    assert len(d["notifications"])==6
    assert all(r["status"]=="cancelled" for r in d["reminders"])
    assert next(b for b in d["bookings"] if b["id"]==e["reservation_id"])["status"]=="cancelled"

def test_invalid_dates_overlap_and_draft(client,monkeypatch):
    e=event()
    assert client.post("/simulate",headers=headers(),json={**e,"departure":e["arrival"]}).status_code==422
    assert client.post("/simulate",headers=headers(),json=e).status_code==200
    assert client.post("/simulate",headers=headers(),json={**e,"event_id":str(uuid4()),"reservation_id":str(uuid4())}).status_code==409
    monkeypatch.delenv("MISTRAL_API_KEY",raising=False)
    r=client.post("/bookings/arezki-b0/question",headers=headers(),json={"text":"parking ?"})
    assert r.status_code==200
    assert r.json()["sent"] is False
    assert "cour" in r.json()["text"]


def test_supabase_membership_auth(client,monkeypatch):
    import main
    from sqlalchemy.orm import Session
    uid=uuid4()
    with Session(engine) as s,s.begin():
        s.add(main.Membership(user_id=uid,owner="arezki"))
    monkeypatch.setattr(main,"AUTH_MODE","supabase")
    monkeypatch.setattr(main,"verify_supabase_user",lambda token: uid)
    assert client.get("/workspace",headers=headers()).json()["owner"]=="arezki"
    assert client.post("/bookings/sarah-b0/question",headers=headers(),json={"text":"parking"}).status_code==404
    monkeypatch.setattr(main,"verify_supabase_user",lambda token: uuid4())
    assert client.get("/workspace",headers=headers()).status_code==403

def test_supabase_remote_validation(monkeypatch):
    import main,httpx
    from fastapi import HTTPException
    uid=uuid4()
    monkeypatch.setattr(main,"SUPABASE_URL","https://test.supabase.co")
    def response(status,payload):
        return httpx.Response(status,json=payload,request=httpx.Request("GET","https://test.supabase.co/auth/v1/user"))
    monkeypatch.setattr(main.httpx,"get",lambda *a,**k:response(200,{"id":str(uid)}))
    assert main.verify_supabase_user("token")==uid
    monkeypatch.setattr(main.httpx,"get",lambda *a,**k:response(401,{}))
    with pytest.raises(HTTPException) as exc: main.verify_supabase_user("expired")
    assert exc.value.status_code==401
    monkeypatch.setattr(main.httpx,"get",lambda *a,**k:response(503,{}))
    with pytest.raises(HTTPException) as exc: main.verify_supabase_user("token")
    assert exc.value.status_code==503
