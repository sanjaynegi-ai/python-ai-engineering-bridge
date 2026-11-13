# Task 6: Explanation

Answer each question in a few sentences, in your own words. Refer to your code where it helps.

## 1. Validation at the boundary (2 points)

Why does `swap_desk` check the swap rules in the Pydantic model, rather than with `if` statements inside the `POST /swaps` route? Give one concrete benefit.

_Your answer._

## 2. Which errors are `HandoverError`s? (3 points)

`summarise_handover` turns some failures into `HandoverError` and lets others propagate. Which ones, and why does the difference matter to the code that calls it?

_Your answer._

## 3. Debugging (3 points)

What was wrong in `deadlines.py`, and what evidence led you to each problem? How do your own tests protect `longest_streak` from future mistakes?

_Your answer._

## 4. A trade-off (2 points)

Your API keeps swaps in memory. Name one thing that goes wrong when this runs in production, and what you would use instead.

_Your answer._
