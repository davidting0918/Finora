"""
Comprehensive data initialization system for different environments.

This module handles initialization of all necessary data for different deployment
environments (test, staging, prod) including categories, users, and sample data.
"""
import json
import logging

from backend.core.database import MongoAsyncClient
from backend.core.environment import Environment, env_config
from backend.core.model.transaction import category_collection, subcategory_collection, transaction_collection
from backend.core.model.user import user_collection

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataInitializer:
    """Handles data initialization for different environments"""

    def __init__(self, db: MongoAsyncClient):
        self.db = db
        self.environment = env_config.environment

    async def init_categories(self, force: bool = False) -> bool:
        """
        Initialize categories and subcategories from JSON file.

        Args:
            force (bool): Force initialization even if data exists

        Returns:
            bool: True if initialization was performed, False if skipped
        """
        try:
            # Check if data already exists
            existing_categories = await self.db.count_documents(category_collection)
            existing_subcategories = await self.db.count_documents(subcategory_collection)

            if not force and (existing_categories > 0 or existing_subcategories > 0):
                logger.info(
                    f"📦 Categories already exist (categories: {existing_categories}, "
                    f"subcategories: {existing_subcategories}), skipping initialization"
                )
                return False

            # Load categories from JSON
            json_path = env_config.get_data_path("default_categories.json")

            with open(json_path, "r", encoding="utf-8") as file:
                data = json.load(file)

            categories = data.get("categories", [])
            subcategories = data.get("subcategories", [])

            # Clear existing data if force=True
            if force:
                await self.db.delete_many(category_collection, {})
                await self.db.delete_many(subcategory_collection, {})
                logger.info("🧹 Cleared existing categories and subcategories")

            # Insert new data
            if categories:
                await self.db.insert_many(category_collection, categories)
                logger.info(f"✅ Inserted {len(categories)} categories")

            if subcategories:
                await self.db.insert_many(subcategory_collection, subcategories)
                logger.info(f"✅ Inserted {len(subcategories)} subcategories")

            logger.info("🎉 Category initialization completed successfully")
            return True

        except FileNotFoundError:
            logger.error(f"❌ Categories JSON file not found: {json_path}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"❌ Invalid JSON format in categories file: {e}")
            raise
        except Exception as e:
            logger.error(f"❌ Category initialization failed: {e}")
            raise

    async def init_sample_users(self, force: bool = False) -> bool:
        """
        Initialize sample users for staging/test environments.

        Args:
            force (bool): Force initialization even if users exist

        Returns:
            bool: True if initialization was performed, False if skipped
        """
        try:
            # Only initialize sample users in staging/test environments
            if not env_config.get("init_sample_users"):
                logger.info("📦 Sample user creation disabled for this environment")
                return False

            existing_users = await self.db.count_documents(user_collection)

            if not force and existing_users > 0:
                logger.info(f"📦 Users already exist ({existing_users}), skipping user initialization")
                return False

            # Load test users from JSON
            json_path = env_config.get_data_path("staging_data.json")

            with open(json_path, "r", encoding="utf-8") as file:
                data = json.load(file)

            user_data = data["users"]
            # Clear existing users if force=True
            if force:
                await self.db.delete_many(user_collection, {})
                logger.info("🧹 Cleared existing users")

            # Insert sample users
            if user_data:
                await self.db.insert_many(user_collection, user_data)
                logger.info(f"✅ Inserted {len(user_data)} sample users")

            logger.info("🎉 Sample users initialization completed successfully")
            return True
        except FileNotFoundError:
            logger.error(f"❌ Users JSON file not found: {json_path}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"❌ Invalid JSON format in users file: {e}")
            raise
        except Exception as e:
            logger.error(f"❌ Sample users initialization failed: {e}")
            raise

    async def init_sample_transactions(self, force: bool = False) -> bool:
        """
        Initialize sample transactions for staging environment.

        Args:
            force (bool): Force initialization even if transactions exist

        Returns:
            bool: True if initialization was performed, False if skipped
        """
        try:
            # Only initialize sample data in staging environment
            if not env_config.get("init_sample_transactions", False):
                logger.info("📦 Sample data initialization disabled for this environment")
                return False

            existing_transactions = await self.db.count_documents(transaction_collection)

            if not force and existing_transactions > 0:
                logger.info(
                    f"📦 Transactions already exist ({existing_transactions}), skipping transaction initialization"
                )
                return False

            # Load sample transactions from JSON
            json_path = env_config.get_data_path("staging_data.json")

            with open(json_path, "r", encoding="utf-8") as file:
                data = json.load(file)

            # Get transaction_list from JSON
            transactions = data.get("transactions")
            if force:
                await self.db.delete_many(transaction_collection, {})
                logger.info("🧹 Cleared existing transactions")

            # Insert sample transactions
            if transactions:
                await self.db.insert_many(transaction_collection, transactions)
                logger.info(f"✅ Inserted {len(transactions)} sample transactions")

            logger.info("🎉 Sample transactions initialization completed successfully")
            return True

        except FileNotFoundError:
            logger.error(f"❌ Transactions JSON file not found: {json_path}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"❌ Invalid JSON format in transactions file: {e}")
            raise
        except Exception as e:
            logger.error(f"❌ Sample transactions initialization failed: {e}")
            raise


async def init_environment() -> None:
    """
    Initialize data based on current environment configuration.

    This is the main initialization function that should be called during
    application startup. It determines what data to initialize based on
    the current environment.
    """
    db = None
    try:
        db = MongoAsyncClient()
        initializer = DataInitializer(db)

        current_env = env_config.environment
        logger.info(f"🚀 Starting data initialization for environment: {current_env.value}")

        # Always initialize categories (required for all environments)
        await initializer.init_categories()

        # Environment-specific initialization
        if current_env == Environment.TEST:
            logger.info("🧪 Test environment detected - initializing test data")
            pass

        elif current_env == Environment.STAGING:
            logger.info("🎭 Staging environment detected - initializing staging data")
            await initializer.init_sample_users()
            await initializer.init_sample_transactions()

        elif current_env == Environment.PRODUCTION:
            logger.info("🏭 Production environment detected - minimal initialization")
            # Only categories are initialized in production
            pass

        logger.info(f"✨ Environment initialization completed for {current_env.value}")

    except Exception as e:
        logger.error(f"❌ Environment initialization failed: {e}")
        raise
    finally:
        if db:
            await db.close()


async def init_category():
    """
    Initialize categories for testing.
    """
    db = MongoAsyncClient()
    initializer = DataInitializer(db)
    await initializer.init_categories()
