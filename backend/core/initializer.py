"""
Simple category initialization from JSON file for use in FastAPI lifespan
"""
import json
from pathlib import Path
from backend.core.database import MongoAsyncClient
from backend.core.model.transaction import category_collection, subcategory_collection
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def init_category():
    """Initialize categories and subcategories from JSON file if not exists"""
    db = MongoAsyncClient()
    
    try:
        # Check if data already exists
        existing_categories = len(await db.find_many(category_collection, {}))
        existing_subcategories = len(await db.find_many(subcategory_collection, {}))
        
        if existing_categories > 0 or existing_subcategories > 0:
            logger.warning(f"Categories already exist (categories: {existing_categories}, subcategories: {existing_subcategories}), skipping initialization")
            return
        
        # Get path to JSON file
        current_dir = Path(__file__).parent
        json_path = current_dir / "../data/default_categories.json"
        
        with open(json_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        categories = data['categories']
        subcategories = data['subcategories']
        
        # Insert into database
        if categories:
            await db.insert_many(category_collection, categories)
            logger.info(f"✅ Inserted {len(categories)} categories")
        
        if subcategories:
            await db.insert_many(subcategory_collection, subcategories)
            logger.info(f"✅ Inserted {len(subcategories)} subcategories")
        
        logger.info("🎉 Category initialization completed successfully")
        
    except FileNotFoundError:
        logger.error(f"❌ JSON file not found: {json_path}")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"❌ Invalid JSON format: {e}")
        raise
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        raise
    finally:
        await db.close()