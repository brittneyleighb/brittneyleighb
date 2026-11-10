#!/usr/bin/env python3
"""Create a self-hosted, 90-day GitHub contribution signal (no dependencies)."""
from datetime import date, datetime, timedelta, timezone
from html import escape
from pathlib import Path
import json
import math
import os
import sys
import urllib.error
import urllib.request

DAYS = 90
OUTPUT = Path(__file__).resolve().parents[1] / "assets" / "contribution-pulse.svg"
QUERY = """query($login: String!, $from: DateTime!, $to: DateTime!) {
  user(login: $login) {
    contributionsCollection(from: $from, to: $to) {
      contributionCalendar {
        weeks { contributionDays { date contributionCount } }
      }
    }
  }
}"""


def get_days(username: str, token: str, today: date) -> list[tuple[date, int]]:
    start = today - timedelta(days=DAYS - 1)
    variables = {
        "login": username,
        "from": f"{start.isoformat()}T00:00:00Z",
        "to": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    body = json.dumps({"query": QUERY, "variables": variables}).encode("utf-8")
    request = urllib.request.Request(
        "https://api.github.com/graphql",
        data=body,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/vnd.github+json",
            "User-Agent": "brittneyleighb-profile-pulse",
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=25) as response:
        result = json.load(response)
    if result.get("errors"):
        raise RuntimeError("GitHub GraphQL error: " + str(result["errors"]))
    try:
        weeks = result["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
    except (KeyError, TypeError) as error:
        raise RuntimeError("Unexpected GitHub contributionCalendar response") from error
    reported = {}
    for week in weeks:
        for day in week["contributionDays"]:
            d = date.fromisoformat(day["date"])
            count = int(day["contributionCount"])
            if count < 0:
                raise ValueError("Negative GitHub contribution count")
            reported[d] = count
    return [(d, reported.get(d, 0)) for d in (start + timedelta(days=i) for i in range(DAYS))]


def render(days: list[tuple[date, int]], updated: date) -> str:
    if len(days) != DAYS or any(days[i][0] >= days[i + 1][0] for i in range(DAYS - 1)):
        raise ValueError("Expected 90 increasing daily observations")
    counts = [count for _, count in days]
    if any(count < 0 for count in counts):
        raise ValueError("Counts must be nonnegative")
    total = sum(counts)
    maximum = max(counts) or 1
    bars = []
    for i, count in enumerate(counts):
        x = 65 + i * 12
        height = int(105 * math.sqrt(count / maximum)) if count else 0
        y = 185 - height
        if count:
            opacity = min(.95, .35 + count / maximum * .65)
            bars.append(f'<line x1="{x}" y1="185" x2="{x}" y2="{y}" stroke="#7eeba8" stroke-width="3.5" stroke-linecap="round" opacity="{opacity:.2f}"/>')
            bars.append(f'<circle cx="{x}" cy="{y}" r="2.3" fill="#d6ffcb"/>')
        else:
            bars.append(f'<line x1="{x}" y1="185" x2="{x}" y2="183" stroke="#315b48" stroke-width="2"/>')
    def label(d):
        return escape(d.strftime("%b %d").upper())
    subtitle = f"{total:,} PUBLIC CONTRIBUTIONS  /  LAST {DAYS} DAYS"
    return f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="1200" height="258" viewBox="0 0 1200 258" role="img" aria-labelledby="title desc">
<title id="title">GitHub contribution signal, last 90 days</title>
<desc id="desc">{total} public GitHub contributions between {days[0][0].isoformat()} and {days[-1][0].isoformat()}. Each vertical bar represents one day; height scales with the square root of its count.</desc>
<defs><linearGradient id="background" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#080f10"/><stop offset="1" stop-color="#10251b"/></linearGradient></defs>
<rect width="1200" height="258" rx="8" fill="url(#background)"/>
<rect x="1" y="1" width="1198" height="256" rx="8" fill="none" stroke="#526c60" opacity=".65"/>
<g font-family="Consolas,Menlo,Monaco,monospace">
  <g role="img" aria-label="CONTRIBUTION SIGNAL" transform="translate(63 61) scale(0.051 -0.051)" fill="#d8f4df"><path d="M585 128C546 89 511 62 478 47C438 28 390 19 334 20C277 21 232 52 198 111C165 171 148 249 148 344C148 559 213 669 342 675C462 680 508 627 517 512H547V669C513 682 489 690 474 693C440 700 395 704 339 704C253 704 181 672 123 607C63 540 33 452 32 344C31 245 61 160 121 89C181 19 254 -16 339 -16C398 -16 446 -7 484 10C526 29 564 63 599 112Z" transform="translate(0 0)"/><path d="M663 341C663 452 636 541 581 607C527 674 453 707 360 707C273 707 201 675 144 610C85 542 55 454 54 347C53 247 82 162 142 91C203 21 275 -14 360 -14C447 -14 519 20 576 89C634 158 663 242 663 341ZM552 343C552 247 537 171 506 114C473 52 425 21 363 21C231 21 165 130 165 347C165 451 178 530 205 583C237 645 289 676 360 676C427 676 477 643 510 578C538 522 552 444 552 343Z" transform="translate(636 0)"/><path d="M708 689H487V658C524 658 546 655 553 649C572 631 581 605 581 571V174L250 689H50V658H106C124 658 134 650 136 635V117C136 82 127 56 108 40C101 34 79 31 42 31V0H263V31C224 31 202 34 195 41C178 57 170 82 170 117V635L593 -17H616L614 571C614 605 623 631 640 648C647 655 669 658 708 658Z" transform="translate(1382 0)"/><path d="M642 689H40L38 486H67C73 545 89 588 114 613C139 638 185 653 250 656L295 658V31H202V0H480V31H386V658L432 656C497 653 543 638 569 611C595 584 610 543 614 486H644Z" transform="translate(2143 0)"/><path d="M469 54C473 50 474 46 474 42C474 37 469 33 460 31H432L431 -1C537 1 613 1 662 -1V29C626 32 602 40 591 54L386 332C444 336 492 353 528 383C565 416 584 458 584 511C584 564 564 608 524 638C481 671 418 689 337 689H34V658H127V31H34V0H312V31H219L217 327H278ZM482 513C485 408 426 356 304 356H217L219 658H325C426 658 479 610 482 513Z" transform="translate(2839 0)"/><path d="M335 31H242V658H335V689H49V658H143V31H49V0H335Z" transform="translate(3525 0)"/><path d="M637 173C638 232 615 279 570 312C534 338 494 352 449 353C538 368 606 429 606 518C606 622 530 689 402 689H52V658H146V31H52V0H400C557 0 636 58 637 173ZM507 519C507 466 490 425 456 397C430 376 401 365 368 365H237V658H384C466 658 507 612 507 519ZM528 176C528 121 510 81 474 57C448 40 416 31 377 31H237V335H369C409 335 443 325 471 304C508 276 527 233 528 176Z" transform="translate(3933 0)"/><path d="M723 692H503V661C541 661 563 658 570 652C587 636 596 610 596 573V247C596 92 531 15 402 15C276 15 213 84 213 223V661H307V692H32V661H124V219C124 158 145 105 186 60C232 10 294 -15 373 -15C470 -15 538 8 576 54C611 97 629 172 629 279V573C629 608 637 634 654 651C661 658 684 661 723 661Z" transform="translate(4675 0)"/><path d="M642 689H40L38 486H67C73 545 89 588 114 613C139 638 185 653 250 656L295 658V31H202V0H480V31H386V658L432 656C497 653 543 638 569 611C595 584 610 543 614 486H644Z" transform="translate(5450 0)"/><path d="M335 31H242V658H335V689H49V658H143V31H49V0H335Z" transform="translate(6146 0)"/><path d="M663 341C663 452 636 541 581 607C527 674 453 707 360 707C273 707 201 675 144 610C85 542 55 454 54 347C53 247 82 162 142 91C203 21 275 -14 360 -14C447 -14 519 20 576 89C634 158 663 242 663 341ZM552 343C552 247 537 171 506 114C473 52 425 21 363 21C231 21 165 130 165 347C165 451 178 530 205 583C237 645 289 676 360 676C427 676 477 643 510 578C538 522 552 444 552 343Z" transform="translate(6554 0)"/><path d="M708 689H487V658C524 658 546 655 553 649C572 631 581 605 581 571V174L250 689H50V658H106C124 658 134 650 136 635V117C136 82 127 56 108 40C101 34 79 31 42 31V0H263V31C224 31 202 34 195 41C178 57 170 82 170 117V635L593 -17H616L614 571C614 605 623 631 640 648C647 655 669 658 708 658Z" transform="translate(7300 0)"/><path d="M491 220C491 326 416 387 268 403C162 414 109 458 108 534C107 619 154 663 251 665C350 666 399 626 408 526H438V705H410C407 695 400 690 390 690C369 690 325 707 274 707C208 707 152 691 106 659C52 622 25 567 25 498C25 396 96 337 238 320C290 314 331 300 361 275C393 247 409 212 409 168C408 127 391 94 356 69C322 46 281 33 235 32C195 31 138 48 112 69C85 92 69 129 65 183H35L34 24C95 1 150 -10 197 -10C278 -10 345 8 398 43C460 84 491 143 491 220Z" transform="translate(8369 0)"/><path d="M335 31H242V658H335V689H49V658H143V31H49V0H335Z" transform="translate(8910 0)"/><path d="M647 271H415V239H528V120C528 102 527 88 523 80C520 69 501 56 466 44C428 29 392 21 357 22C300 23 255 53 221 112C187 172 170 249 170 345C170 555 235 665 365 673C481 679 530 624 539 510H569V667C531 682 506 690 495 692C462 700 417 704 360 704C275 704 204 672 145 607C86 539 56 453 55 345C54 246 83 161 142 90C204 21 275 -14 360 -14C419 -14 468 -8 509 2C544 13 578 25 613 35V239H647Z" transform="translate(9318 0)"/><path d="M708 689H487V658C524 658 546 655 553 649C572 631 581 605 581 571V174L250 689H50V658H106C124 658 134 650 136 635V117C136 82 127 56 108 40C101 34 79 31 42 31V0H263V31C224 31 202 34 195 41C178 57 170 82 170 117V635L593 -17H616L614 571C614 605 623 631 640 648C647 655 669 658 708 658Z" transform="translate(10041 0)"/><path d="M725 31H651L415 708H375L158 138C139 85 120 53 103 42C90 34 66 30 31 31V0H249V31C211 31 190 34 186 40C182 46 180 54 180 63C180 82 186 107 198 138L236 228H477L545 31H465V0H725ZM250 266 364 559 463 266Z" transform="translate(10802 0)"/><path d="M570 239C567 172 545 120 506 83C493 70 473 59 446 49C420 39 398 34 380 34L227 31V658H321V689H44V658H138V31H44V0H589L602 239Z" transform="translate(11578 0)"/></g>
  <text x="1135" y="41" fill="#9cc3a9" font-size="12" text-anchor="end">GITHUB / PUBLIC ACTIVITY</text>
  <text x="64" y="66" fill="#8fbba2" font-size="12" letter-spacing="1.4">{escape(subtitle)}</text>
  <path d="M65 185H1135" stroke="#527c62" stroke-width="1" opacity=".65"/>
  {''.join(bars)}
  <text x="65" y="217" fill="#8fbba2" font-size="13">{label(days[0][0])}</text>
  <text x="599" y="217" fill="#8fbba2" font-size="13" text-anchor="middle">{label(days[DAYS // 2][0])}</text>
  <text x="1135" y="217" fill="#8fbba2" font-size="13" text-anchor="end">{label(days[-1][0])}</text>
  <text x="65" y="243" fill="#759c89" font-size="11">COMMITS · ISSUES · PULL REQUESTS · REVIEWS · OTHER CONTRIBUTIONS</text>
  <text x="1135" y="243" fill="#759c89" font-size="11" text-anchor="end">UPDATED {updated.isoformat()} UTC</text>
</g>
</svg>
'''


def main() -> None:
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        sys.exit("GITHUB_TOKEN is required; refusing to fabricate activity data")
    username = os.environ.get("GITHUB_USERNAME", "brittneyleighb")
    today = datetime.now(timezone.utc).date()
    try:
        days = get_days(username, token, today)
    except (urllib.error.URLError, RuntimeError, ValueError) as error:
        sys.exit(f"Could not update contribution signal: {error}")
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(render(days, today), encoding="utf-8")
    print(f"Updated {OUTPUT} from GitHub contributionCalendar")


if __name__ == "__main__":
    main()
