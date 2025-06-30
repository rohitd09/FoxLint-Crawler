# 🕷️ FoxLint: Privacy Policy & Terms Crawler

This is a web crawler built with **Scrapy** and **Playwright** to automatically navigate websites and extract paths to their **Privacy Policy** and **Terms of Service** pages.

---

## 📦 Features

- Uses Playwright for rendering JavaScript-heavy websites
- Supports dynamic page discovery
- Configurable target domains
- Easy deployment and environment setup via Conda

---

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/foxlint.git
cd foxlint
```

---

### 2. Setup Conda Environment

```bash
conda env create -f environment.yml
conda activate foxlint
playwright install
```

---

## 🕷️ Running the Crawler

To run the spider on the default input:

```bash
scrapy crawl policy_spider
```

To specify a custom input file or domain list:

```bash
scrapy crawl policy_spider -a input_file=subdirectories.csv
```

---

## 📁 Project Structure

```
foxlint/
├── spiders/
│   └── policy_spider.py
├── subdirectories.csv
├── environment.yml
├── .gitignore
├── scrapy.cfg
└── README.md
```

---

## ❗ Limitations

- **robots.txt Restrictions**: Some websites explicitly disallow crawling important pages. You may disable `ROBOTSTXT_OBEY = True` in `settings.py` to bypass this, but only as a last resort and at your own risk.
- **Bot Detection**: Some websites use advanced bot detection (e.g., Cloudflare, CAPTCHA) and cannot be crawled even with Playwright.
- **News Websites**: Domains like news publishers tend to have many URLs matching common legal keyword patterns (e.g., `/privacy`, `/terms`) leading to noise and false positives.
- **Dynamic Content**: Some policies are loaded via embedded iframes or AJAX calls and may not be directly extractable.

---

## 🛑 .gitignore

Make sure to add the following to your `.gitignore`:

```
__pycache__/
spiders/__pycache__/
.env
```

---

## 🛠️ Troubleshooting

- **Playwright Timeout**: If you experience timeouts, consider increasing the timeout in your `meta`:
  ```python
  meta={
    "playwright": True,
    "playwright_page_goto_kwargs": {"timeout": 60000},
  }
  ```
- **Missing Browsers**: Run `playwright install` again.
- **Permission Issues**: Run with elevated privileges or fix file permissions.

---