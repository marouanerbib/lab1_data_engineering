"""
Data validation and analysis script for extracted Google Play Store data.

Validates the structure and provides summary statistics for:
- apps_metadata_raw.json
- user_reviews_raw.jsonl
"""

import json
from pathlib import Path
from collections import defaultdict
from datetime import datetime

def validate_metadata(filepath: str) -> None:
    """Validate and display metadata file statistics."""
    print("\n" + "="*70)
    print("APP METADATA VALIDATION & SUMMARY")
    print("="*70)
    
    with open(filepath, 'r') as f:
        apps = json.load(f)
    
    print(f"\nTotal apps: {len(apps)}")
    print("\nApps extracted:")
    print("-" * 70)
    
    for i, app in enumerate(apps, 1):
        print(f"\n{i}. {app['title']}")
        print(f"   ID: {app['appId']}")
        print(f"   Developer: {app['developer']}")
        print(f"   Rating: {app['score']:.2f}/5 ({app['ratings']:,} ratings)")
        print(f"   Reviews: {app['reviews']:,}")
        print(f"   Installs: {app['installs']}")
        print(f"   Free: {app['free']}")
        print(f"   Categories: {', '.join([c.get('name', 'Unknown') for c in app.get('categories', [])])}")
        print(f"   Updated: {datetime.fromtimestamp(app['updated']).strftime('%Y-%m-%d')}")
    
    # Aggregate statistics
    print("\n" + "-" * 70)
    print("AGGREGATE STATISTICS")
    print("-" * 70)
    
    ratings_count = sum(app['ratings'] for app in apps)
    avg_score = sum(app['score'] * app['ratings'] for app in apps) / ratings_count if ratings_count > 0 else 0
    total_reviews = sum(app['reviews'] for app in apps)
    
    print(f"Total ratings across all apps: {ratings_count:,}")
    print(f"Weighted average score: {avg_score:.2f}/5")
    print(f"Total reviews on Play Store: {total_reviews:,}")
    print(f"Average installs (parsed): {ratings_count / len(apps):,.0f}")
    
    # Rating distribution
    print("\nRating distribution (1-5 stars):")
    for app in apps:
        if 'histogram' in app:
            histogram = app['histogram']
            total = sum(histogram)
            print(f"\n  {app['title']}:")
            labels = ['1★', '2★', '3★', '4★', '5★']
            for label, count in zip(labels, histogram):
                pct = (count / total * 100) if total > 0 else 0
                bar = '█' * int(pct / 2)
                print(f"    {label} {count:>7,} ({pct:>5.1f}%) {bar}")


def validate_reviews(filepath: str, sample_size: int = 100) -> None:
    """Validate and display reviews file statistics."""
    print("\n\n" + "="*70)
    print("REVIEWS DATA VALIDATION & SUMMARY")
    print("="*70)
    
    # Count total lines
    total_lines = sum(1 for _ in open(filepath))
    print(f"\nTotal reviews: {total_lines:,}")
    
    # Collect statistics
    app_review_counts = defaultdict(int)
    score_distribution = defaultdict(int)
    rating_stats = []
    thumbs_up_stats = []
    
    print("\nAnalyzing reviews...")
    with open(filepath, 'r') as f:
        for i, line in enumerate(f):
            if i % 1000 == 0:
                print(f"  Processed {i:,} reviews...", end='\r')
            
            review = json.loads(line)
            app_id = review['appId']
            app_review_counts[app_id] += 1
            score_distribution[review['score']] += 1
            rating_stats.append(review['score'])
            thumbs_up_stats.append(review['thumbsUpCount'])
    
    print(f"  Processed {total_lines:,} reviews...      ")
    
    # Display per-app statistics
    print("\nReviews per app:")
    print("-" * 70)
    for app_id in sorted(app_review_counts.keys()):
        count = app_review_counts[app_id]
        print(f"  {app_id}: {count:,} reviews")
    
    # Rating distribution
    print("\nRating distribution (all apps):")
    print("-" * 70)
    total = sum(score_distribution.values())
    for rating in sorted(score_distribution.keys()):
        count = score_distribution[rating]
        pct = (count / total * 100)
        bar = '█' * int(pct / 2)
        print(f"  {rating}★ {count:>6,} ({pct:>5.1f}%) {bar}")
    
    # Summary statistics
    avg_score = sum(rating_stats) / len(rating_stats) if rating_stats else 0
    avg_thumbs_up = sum(thumbs_up_stats) / len(thumbs_up_stats) if thumbs_up_stats else 0
    max_thumbs_up = max(thumbs_up_stats) if thumbs_up_stats else 0
    
    print("\nOverall statistics:")
    print("-" * 70)
    print(f"Average rating: {avg_score:.2f}/5")
    print(f"Average thumbs up count: {avg_thumbs_up:.2f}")
    print(f"Max thumbs up: {max_thumbs_up}")
    
    # Show sample reviews
    print("\nSample reviews (first 3):")
    print("-" * 70)
    with open(filepath, 'r') as f:
        for i in range(min(3, total_lines)):
            review = json.loads(f.readline())
            print(f"\nReview {i+1}:")
            print(f"  App: {review['appId']}")
            print(f"  User: {review['userName']}")
            print(f"  Rating: {review['score']}/5")
            print(f"  Date: {review['at']}")
            print(f"  Thumbs Up: {review['thumbsUpCount']}")
            print(f"  Content: {review['content'][:100]}..." if len(review['content']) > 100 else f"  Content: {review['content']}")


def validate_jsonl_format(filepath: str) -> bool:
    """Validate JSONL file format (one JSON per line)."""
    print("\n\n" + "="*70)
    print("JSONL FORMAT VALIDATION")
    print("="*70)
    
    errors = 0
    with open(filepath, 'r') as f:
        for i, line in enumerate(f):
            try:
                json.loads(line)
            except json.JSONDecodeError as e:
                print(f"Error on line {i+1}: {e}")
                errors += 1
    
    if errors == 0:
        print(f"\n✓ All {i+1} lines are valid JSON")
        return True
    else:
        print(f"\n✗ Found {errors} invalid JSON lines out of {i+1}")
        return False


def main():
    """Main validation script."""
    metadata_file = Path('apps_metadata_raw.json')
    reviews_file = Path('user_reviews_raw.jsonl')
    
    if not metadata_file.exists():
        print(f"Error: {metadata_file} not found")
        return
    
    if not reviews_file.exists():
        print(f"Error: {reviews_file} not found")
        return
    
    # Validate metadata
    validate_metadata(str(metadata_file))
    
    # Validate reviews
    validate_reviews(str(reviews_file))
    
    # Validate JSONL format
    validate_jsonl_format(str(reviews_file))
    
    print("\n\n" + "="*70)
    print("VALIDATION COMPLETE")
    print("="*70)
    print("\nFiles ready for analysis:")
    print(f"  ✓ {metadata_file} ({metadata_file.stat().st_size / 1024:.1f} KB)")
    print(f"  ✓ {reviews_file} ({reviews_file.stat().st_size / 1024 / 1024:.1f} MB)")
    print("="*70 + "\n")


if __name__ == '__main__':
    main()
