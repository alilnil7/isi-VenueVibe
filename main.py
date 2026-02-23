from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from Core_Engine import core_engine
import stripe

app = FastAPI(title="VenueVibe API")

class SubmissionRequest(BaseModel):
    url: str
    bid: float

@app.post("/submit")
async def submit_song(request: SubmissionRequest):
    try:
        session_id = core_engine.submit_song(request.url, request.bid)
        return {"checkout_session_id": session_id}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/queue")
async def get_queue():
    return core_engine.get_queue()

@app.get("/next-song")
async def get_next_song():
    song = core_engine.pop_next()
    if not song:
        return {"message": "Queue is empty"}
    return song

@app.post("/webhook/stripe")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        from stripe_client import stripe_client
        event = stripe_client.verify_webhook(payload, sig_header)
        
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            core_engine.confirm_payment(session['id'])
            
        return {"status": "success"}
    except Exception as e:
        # In mock mode, we might want to manually confirm for testing
        raise HTTPException(status_code=400, detail=f"Webhook error: {str(e)}")

# For testing purposes - manual confirmation endpoint
@app.get("/test/confirm/{session_id}")
async def test_confirm(session_id: str):
    success = core_engine.confirm_payment(session_id)
    if success:
        return {"status": "Song added to queue"}
    return {"status": "Failed to confirm or already confirmed"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
