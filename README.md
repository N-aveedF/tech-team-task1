 CSI SCT SB - Tech Team Task 1: URL Shortener

This is a responsive, Bitly-like URL shortening service built with **FastAPI** and **SQLite**. It fulfills all core requirements and several optional bonus features.

 **Live Demo:** [Insert your live link here once hosted - or remove this line]

##  Features Implemented
* Generate short URLs from long URLs
* Redirect short URLs to original destinations
* Prevent collisions & handle invalid URLs
* Bonus: Custom aliases support
* Bonus: Link expiration dates
* Bonus: Rate limiting (Max 5 per minute)
* Bonus: Real-time analytics tracking (Total visits & timestamp history)

##  How to Test
1. Enter a long URL in the Create Link card.
2. (Optional) Add a custom alias or expiration date. 
3. Click Generate! 
4. To view analytics, enter your short code in the Link Analytics card to see the visit count and timestamp history.

##  How to Run Locally
If you prefer to run the code on your own machine:
1. Clone this repository.
2. Install dependencies: `pip install -r requirements.txt`
3. Run the server: `python -m uvicorn counter:app --reload`
4. Open `http://127.0.0.1:8000` in your browser.
