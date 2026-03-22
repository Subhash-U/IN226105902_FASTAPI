# TrendZone Fashion Store API

This is a backend project built using **FastAPI** as part of a 6-day internship training. It simulates a fashion store with products, orders, and wishlist functionality.

## Project Overview

**What it does:**
- Allows users to browse fashion products.
- Users can place orders with validation (Pydantic models).
- Wishlist management with multi-step workflow (add → remove → order all).
- Advanced search, filtering, sorting, and pagination.
- Business logic handled via helper functions (e.g., order total calculation, discounts).
- CRUD operations for products.

**Key Features:**
- GET endpoints for listing products, summary, and individual product details.
- POST endpoints with request body validation (Field, min_length, gt, le).
- Full CRUD operations: Create, Update, Delete products.
- Helper functions for calculations and filtering.
- Multi-step workflows: wishlist → order processing.
- Search across multiple fields: name, brand, category.
- Sorting and pagination with metadata.
- Error handling using HTTPException.

## Tech Stack
- Python 3.11+
- FastAPI
- Pydantic
- Uvicorn (ASGI server)

## Installation

1. Clone the repository:
```bash
git clone <your-github-repo-link>
cd fashion-store-api
