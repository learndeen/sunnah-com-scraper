# Sunnah.com Scraper

A robust Python scraper to extract hadith collections, books, and individual narrations from [Sunnah.com](https://sunnah.com).

## Features
- **Comprehensive Scraping**: Extracts collections (e.g., Sahih Bukhari), books, and hadiths.
- **Bilingual**: Captures both English and Arabic text.
- **Metadata Rich**: Preserves reference numbers and chapter headers.
- **Structured Output**: Saves data in clean, easy-to-parse JSON files.
- **Resilient**: Handles network requests with error checking and respect for the server (politeness delays).

## Prerequisites
- **Python 3.7+**
- **pip** (Python package installer)

## Installation

1.  **Clone the repository** (if applicable) or download the source code.
2.  **Install dependencies**:
    ```bash
    pip3 install -r requirements.txt
    ```

## Usage

Run the scraper using the command line interface:

```bash
python3 scraper.py [OPTIONS]
```

### Options
- `--collections N`: Limit the number of collections to scrape (default: 1).
- `--books N`: Limit the number of books to scrape per collection (default: 1).
- `--all`: Scrape ALL collections and ALL books (overrides limits). WARNING: This is a large amount of data.

## Demo Steps

Follow these steps to quickly verify the scraper works as expected:

### 1. Quick Test
Run a minimal scrape to fetch just the first book of the first collection (Sahih al-Bukhari).
```bash
python3 scraper.py --collections 1 --books 1
```

**Expected Output:**
```text
Starting scraper...
Found 17 collections.

Processing Collection: Sahih al-Bukhariصحيح البخاري
Found 97 books in Sahih al-Bukhariصحيح البخاري.
  Scraping Book 1: 1Revelationكتاب بدء الوحى
  Found 7 hadiths.
```

### 2. Check the Data
Navigate to the `data` directory and inspect the generated JSON file.
```bash
ls -l data/
cat data/bukhari_1.json
```
You should see a JSON file containing the hadiths from the "Revelation" chapter, including Arabic text like "‎إنما الأعمال بالنيات" and its English translation.

### 3. Slightly Larger Scrape
To scrape the first 3 books of the first 2 collections:
```bash
python3 scraper.py --collections 2 --books 3
```

### 4. Scrape Specific Collections
You can scrape a specific collection using the `--slug` argument.

**Sahih Muslim (First 2 books):**
```bash
python3 scraper.py --slug muslim --books 2
```
**Expected Output:**
```text
Processing Collection: Sahih Muslimصحيح مسلم
Found 57 books in Sahih Muslimصحيح مسلم.
  Scraping Book introduction: Introductionالمقدمة
  Found 91 hadiths.
  Scraping Book 1: 1The Book of Faithكتاب الإيمان
  Found 439 hadiths.
```

**Muwatta Malik (First book):**
```bash
python3 scraper.py --slug malik --books 1
```
**Expected Output:**
```text
Processing Collection: Muwatta Malikموطأ مالك
Found 61 books in Muwatta Malikموطأ مالك.
  Scraping Book 1: 1The Times of Prayerكتاب وقوت الصلاة
  Found 31 hadiths.
```
*Note: Using `--all` without `--slug` will scrape the ENTIRE website.*

### 5. Common Collection Slugs
| Collection | Slug |
|Data Source|Slug|
|---|---|
|Sahih al-Bukhari|`bukhari`|
|Sahih Muslim|`muslim`|
|Sunan an-Nasa'i|`nasai`|
|Sunan Abi Dawud|`abudawud`|
|Jami' at-Tirmidhi|`tirmidhi`|
|Sunan Ibn Majah|`ibnmajah`|
|Muwatta Malik|`malik`|
|40 Hadith Nawawi|`nawawi40`|
|Riyad as-Salihin|`riyadussalihin`|

## Output Structure

The data is saved in `data/{collection_slug}_{book_number}.json`.
**Example Structure:**
```json
{
  "collection": {
    "name": "Sahih al-Bukhari",
    "slug": "bukhari",
    "url": "https://sunnah.com/bukhari"
  },
  "book": {
    "number": "1",
    "title": "Revelation",
    "url": "https://sunnah.com/bukhari/1"
  },
  "hadiths": [
    {
      "text_en": "Narrated 'Umar bin Al-Khattab...",
      "text_ar": "...",
      "references": { ... }
    }
  ]
}
```
