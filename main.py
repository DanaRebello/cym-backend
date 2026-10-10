"""
Entry point. Runs an end-to-end demo using FakeRepository.
Swap to SQLiteRepository (teammate's) when ready.
"""

from fake_repository import FakeRepository
# from sqlite_repository import SQLiteRepository   # <- teammate's, swap in later

from conversation import handle_message


def run_demo():
    repo = FakeRepository()

    print("=" * 60)
    print("AI REAL ESTATE LEAD QUALIFICATION — DEMO")
    print("=" * 60)

    buyer_id = repo.create_buyer("Ananya", phone="+91-9000000000")
    print(f"Created buyer: {buyer_id}\n")

    turns = [
        "Hi, I'm looking for a 3 BHK apartment in Kakkanad.",
        "My budget is around 80 lakh. I want to buy within 2 weeks.",
        "I have a pre-approved loan.",
    ]

    for msg in turns:
        print(f"BUYER: {msg}")
        reply = handle_message(repo, buyer_id, msg)
        print(f"AI   : {reply}\n")

    qual = repo.get_latest_qualification(buyer_id)
    print("=" * 60)
    print("FINAL QUALIFICATION")
    print("=" * 60)
    if qual:
        for k, v in qual.items():
            print(f"  {k:.<28} {v}")
    else:
        print("  No qualification saved.")

    # --- Second scenario: ambiguous lead ---
    print("\n" + "=" * 60)
    print("SCENARIO 2: vague high-budget lead")
    print("=" * 60)
    bid2 = repo.create_buyer("Mr. Verma")
    for msg in [
        "I want something in Kochi. Budget is 40 crores.",
    ]:
        print(f"BUYER: {msg}")
        print(f"AI   : {handle_message(repo, bid2, msg)}\n")


if __name__ == "__main__":
    run_demo()