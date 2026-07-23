# Requirements Document

## 1. Application Overview

**Application Name**: Har Ghar Solar Platform Enhancement

**Description**: Enhancement of existing Flask-based solar information platform (https://hargharsolar.duckdns.org) to achieve Google AdSense approval and SEO optimization while maintaining all current features, branding (green theme #005B38), and tech stack (Flask + SQLAlchemy + SQLite + Jinja2 + Bootstrap 5).

## 2. Users and Usage Scenarios

**Target Users**:
- Homeowners seeking solar installation information
- Vendors managing leads and quotations
- Administrators managing platform operations
- Search engine users discovering solar content

**Core Scenarios**:
- Users read blog articles about solar solutions and subsidies
- Users submit lead generation forms
- Users calculate solar costs and subsidies
- Vendors manage quotations and coverage areas
- Admins manage leads, vendors, and reports

## 3. Page Structure and Functionality

### 3.1 Page Hierarchy

```
Existing Pages (Preserve)
├── Home (/)
├── Lead Form
├── Solar Calculator
├── Subsidy Calculator
├── Admin Panel
│   ├── Login
│   ├── Lead Management
│   ├── Vendor Management
│   ├── Quotations
│   └── Reports
├── Vendor Portal
│   ├── Login
│   ├── Profile
│   ├── Pricing
│   ├── Coverage
│   ├── Quotations
│   └── Performance
├── About (/about)
└── Contact (/contact)

New Pages (Add)
├── Blog System
│   ├── Blog Listing (/blog)
│   ├── Article Detail (/blog/<slug>)
│   ├── Category Listing (/blog/category/<category>)
│   ├── Tag Listing (/blog/tag/<tag>)
│   └── Blog Search (/blog/search)
├── Trust Pages
│   ├── Privacy Policy (/privacy-policy)
│   ├── Cookie Policy (/cookie-policy)
│   ├── Disclaimer (/disclaimer)
│   ├── Terms & Conditions (/terms)
│   ├── Editorial Policy (/editorial-policy)
│   ├── Our Mission (/our-mission)
│   ├── Why Trust Us (/why-trust-us)
│   └── How We Verify (/how-we-verify)
├── Search (/search)
├── Sitemap (/sitemap.xml)
├── Robots (/robots.txt)
└── RSS Feed (/rss.xml)
```

### 3.2 Blog System

**3.2.1 Blog Database Model**
- Fields: id, title, slug, content, meta_title, meta_desc, category, tags, author, reading_time, published_at, updated_at, featured_image, schema_markup, is_published
- Store 100 articles covering PM Surya Ghar Yojana, Solar Subsidy (UP/India), Solar Cost (1kW/2kW/3kW/5kW/10kW), On Grid vs Off Grid vs Hybrid, Net Metering, Panel Cleaning, Maintenance, EMI Guide, Installation Process, Panel Efficiency, Warranty, Best Brands, Government Schemes, Residential/Commercial Guides, FAQs, Battery Guide, Inverter Guide, MNRE Guidelines, Safety, Rooftop Benefits, ROI Calculator Guide, Loan Guide, Solar Myths, and 70+ related sub-topics

**3.2.2 Blog Listing Page (/blog)**
- Display article cards with title, excerpt, category, tags, reading time, published date, featured image
- Category filter navigation
- Tag cloud
- Popular posts sidebar
- Pagination

**3.2.3 Article Detail Page (/blog/<slug>)**
- Article content (1200-1800 words)
- H1/H2/H3 heading structure
- Table of contents
- FAQ accordion section
- Comparison tables where applicable
- Internal links to related articles
- CTA (call-to-action) for lead form
- Author box
- Last updated timestamp
- Related posts section
- AdSense ad placements (above fold, in-article, below content)
- Schema markup (Article, FAQ)

**3.2.4 Category/Tag Pages**
- List articles filtered by category or tag
- Breadcrumb navigation
- Meta tags optimized for category/tag

**3.2.5 Blog Search**
- Search within blog articles by title, content, tags
- Display results with relevance ranking

### 3.3 Trust Pages

**3.3.1 About Us (/about)**
- Improve existing page with mission statement, team information, company background

**3.3.2 Privacy Policy (/privacy-policy)**
- GDPR and AdSense compliant privacy policy
- Data collection, usage, storage, sharing practices
- Cookie usage disclosure
- User rights and contact information

**3.3.3 Cookie Policy (/cookie-policy)**
- Types of cookies used
- Purpose of each cookie
- User consent mechanism

**3.3.4 Disclaimer (/disclaimer)**
- Information accuracy disclaimer
- No warranty statements
- Limitation of liability

**3.3.5 Terms & Conditions (/terms)**
- User agreement terms
- Service usage rules
- Intellectual property rights
- Dispute resolution

**3.3.6 Editorial Policy (/editorial-policy)**
- Content creation standards
- Fact-checking process
- Source verification methods
- Editorial independence statement

**3.3.7 Contact (/contact)**
- Improve existing page with contact form, email, phone, address

**3.3.8 Our Mission (/our-mission)**
- Platform mission and vision
- Solar adoption goals
- Community impact

**3.3.9 Why Trust Us (/why-trust-us)**
- Credentials and expertise
- Industry partnerships
- User testimonials
- Certifications

**3.3.10 How We Verify (/how-we-verify)**
- Information verification process
- Source credibility standards
- Update frequency
- Expert review process

### 3.4 Enhanced Existing Features

**3.4.1 Subsidy Calculator Enhancement**
- Add state-wise selection dropdown (currently supports 75 UP districts, maintain this)
- Display applicable subsidy amounts based on state and capacity

**3.4.2 Solar Comparison Tables**
- On-grid vs Off-grid vs Hybrid comparison table component
- Display differences in cost, benefits, maintenance, ROI

**3.4.3 Savings Calculator**
- Input: monthly electricity bill
- Output: estimated monthly/annual savings with solar
- Display payback period

**3.4.4 EMI Calculator**
- Input: loan amount, interest rate, tenure
- Output: monthly EMI, total interest, total payment

**3.4.5 Installation Timeline Visual**
- Display step-by-step installation process with estimated timeframes

**3.4.6 FAQ Accordion Component**
- Reusable Jinja2 partial for FAQ sections
- Collapsible/expandable question-answer pairs
- Schema markup for FAQ

**3.4.7 Downloadable PDF Guide Pages**
- Content-rich guide pages (not actual PDF generation)
- Topics: Solar Installation Guide, Subsidy Application Guide, Maintenance Guide

### 3.5 SEO and Technical Pages

**3.5.1 Sitemap (/sitemap.xml)**
- Dynamic XML sitemap including all blog posts and static pages
- Update frequency and priority tags

**3.5.2 Robots.txt (/robots.txt)**
- Allow search engine crawling
- Disallow admin and vendor portal paths
- Reference sitemap location

**3.5.3 RSS Feed (/rss.xml)**
- RSS 2.0 format feed of blog articles
- Include title, description, link, publication date

**3.5.4 Search Page (/search)**
- Full-text search across all public pages and blog articles
- Display results with title, excerpt, URL

**3.5.5 Error Pages**
- Custom templates for 404, 500, 403, 400, 429 errors
- Branded design consistent with site theme
- Navigation links to return to main sections

### 3.6 SEO Enhancements

**3.6.1 Meta Tags (All Pages)**
- Unique meta title (50-60 characters)
- Unique meta description (150-160 characters)
- Canonical URL
- Open Graph tags (og:title, og:description, og:image, og:url, og:type)
- Twitter Card tags (twitter:card, twitter:title, twitter:description, twitter:image)

**3.6.2 Structured Data**
- Organization schema on homepage
- LocalBusiness schema on contact page
- Breadcrumb schema on all pages
- Article schema on blog posts
- FAQ schema on pages with FAQ sections

**3.6.3 Navigation Enhancement**
- Add Blog link to main navigation menu
- Breadcrumb navigation on all pages

**3.6.4 Search Console Integration**
- Placeholder meta tag for Google Search Console verification
- Placeholder meta tag for Bing Webmaster Tools verification

### 3.7 AdSense Integration

**3.7.1 Ad Placements**
- Publisher ID: ca-pub-2051033451758355
- Blog article pages: above fold ad unit, in-article ad unit, below content ad unit
- Strategic placement on high-traffic pages

**3.7.2 Footer Links Fix**
- Update Privacy Policy link from /contact to /privacy-policy
- Update Terms link from /contact to /terms

### 3.8 UX Improvements

**3.8.1 Accessibility**
- ARIA labels on interactive elements
- Skip-to-content link
- Proper heading hierarchy (H1 → H2 → H3)
- Color contrast compliance (WCAG AA)

**3.8.2 Performance Optimization**
- Lazy loading on all non-critical images (loading=\"lazy\")
- Preload critical fonts and CSS
- Loading skeleton for dynamic content sections
- Minified inline CSS and JavaScript

**3.8.3 Static Assets**
- /static/manifest.json for PWA metadata
- /static/browserconfig.xml for Windows tile configuration

## 4. Business Rules and Logic

### 4.1 Blog Article Rules
- Each article must be 1200-1800 words
- Must include H1 (title), H2 (sections), H3 (sub-sections)
- Must include FAQ section with minimum 3 questions
- Must include at least 2 internal links to related articles
- Must include CTA linking to lead form or calculator
- Reading time calculated as word count / 200 words per minute
- Schema markup generated automatically based on article structure

### 4.2 SEO Rules
- Meta title must be unique per page, 50-60 characters
- Meta description must be unique per page, 150-160 characters
- Canonical URL must match current page URL
- Sitemap updated automatically when new blog post published
- Robots.txt allows all except /admin and /vendor paths

### 4.3 AdSense Compliance Rules
- No duplicate meta tags across pages
- No thin content (minimum 300 words per page)
- No empty pages or placeholder text
- All trust pages must contain real, complete content
- Privacy Policy and Terms must be accessible from footer on all pages

### 4.4 Search Functionality
- Blog search searches within title, content, tags, category
- Global search searches across all public pages and blog articles
- Results ranked by relevance (title match > content match)

### 4.5 Data Preservation
- All existing database models preserved: Lead, Vendor, VendorProfile, VendorPricing, VendorQuotation, User
- All existing features preserved: lead form, calculators, admin panel, vendor portal, email notifications
- 75 UP districts support maintained

## 5. Exceptions and Edge Cases

| Scenario | Handling |
|----------|----------|
| Blog article slug conflict | Append numeric suffix to slug |
| Search query returns no results | Display \"No results found\" message with suggestions |
| Featured image missing for blog post | Use default placeholder image |
| AdSense ad unit fails to load | Display empty space, no error message |
| Sitemap generation fails | Log error, serve cached version |
| RSS feed request for unpublished articles | Exclude unpublished articles from feed |
| User accesses /blog/<invalid-slug> | Return 404 error page |
| Database query timeout on search | Return partial results with timeout notice |
| Schema markup generation error | Log error, page still renders without schema |

## 6. Acceptance Criteria

1. User visits homepage, clicks Blog link in navigation, views blog listing page with article cards
2. User clicks on article card, reads full article with table of contents, FAQ section, and related posts
3. User clicks CTA button in article, navigates to lead form, submits lead successfully
4. User visits /privacy-policy, reads complete privacy policy content
5. User visits /sitemap.xml, sees XML sitemap with all blog posts and static pages
6. User performs search via /search, enters query, views relevant results
7. Administrator logs into admin panel, views new blog management section, publishes new article
8. Search engine crawler accesses /robots.txt, receives proper directives and sitemap reference

## 7. Out of Scope for This Phase

- Actual PDF file generation for downloadable guides
- Multi-language support beyond English
- User authentication for blog commenting
- Social media sharing analytics tracking
- A/B testing for ad placements
- Automated content generation for blog articles
- Integration with external CMS platforms
- Mobile app development
- Real-time chat support
- Payment gateway integration for solar products
- Vendor rating and review system
- Advanced analytics dashboard beyond existing reports
- Email marketing automation
- Push notification system
- Video content hosting and streaming
- Interactive solar panel 3D visualization