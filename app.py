
# --- Simplified app.py with JWT auto-refresh injection ---

import json
import requests
import asyncio
import threading

# ==============================
# 🔥 TOKEN REFRESH FUNCTION
# ==============================

def refresh_tokens_from_jwt():
    print("🔄 Refreshing tokens...")

    try:
        with open("Guest.json", "r") as f:
            guests = json.load(f)
    except:
        print("Guest.json error")
        return

    for acc in guests:
        uid = acc.get("uid")

        try:
            res = requests.get(f"https://only-jwt.vercel.app/token?uid={uid}")

            if res.status_code != 200:
                continue

            new_token = res.json().get("token")
            if not new_token:
                continue

            for file in ["token_ind.json", "token_ind_visit.json"]:
                try:
                    with open(file, "r") as f:
                        data = json.load(f)

                    for entry in data:
                        if str(entry.get("uid")) == str(uid):
                            entry["token"] = new_token
                            break

                    with open(file, "w") as f:
                        json.dump(data, f, indent=2)

                except:
                    pass

            print(f"✅ Updated UID {uid}")

        except Exception as e:
            print("JWT error:", e)

    print("✅ All tokens refreshed")


# ==============================
# 🔥 EXAMPLE LIKE FLOW (PATCH POINT)
# ==============================

def handle_like_logic(player_nickname_from_profile,
                      tokens_for_like_sending,
                      uid_param,
                      server_name_param,
                      like_api_url,
                      send_likes_with_token_batch):

    # TOKEN EXPIRE DETECTION
    if not player_nickname_from_profile or player_nickname_from_profile.strip().upper() == "N/A":
        print("⚠️ Token expired → refreshing...")

        refresh_tokens_from_jwt()

        print("🔁 Retrying like...")

        if tokens_for_like_sending:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(
                    send_likes_with_token_batch(
                        uid_param,
                        server_name_param,
                        like_api_url,
                        tokens_for_like_sending
                    )
                )
            finally:
                loop.close()
