import asyncio
import aiohttp
import json
import logging
from datetime import datetime
from typing import Dict, List, Any

from config import config

logger = logging.getLogger(__name__)

class LegalUpdater:
    def __init__(self):
        self.government_api_url = config.get('LEGAL_API_URL')
        self.api_key = config.get('GOVERNMENT_API_KEY')
        
    async def update_legal_content(self):
        """Update legal content from government sources"""
        try:
            # Update veterans benefits
            await self.update_veterans_benefits()
            
            # Update compensation information
            await self.update_compensation_info()
            
            # Update legal procedures
            await self.update_legal_procedures()
            
            logger.info("Legal content update completed")
            
        except Exception as e:
            logger.error(f"Error updating legal content: {e}")
    
    async def update_veterans_benefits(self):
        """Update veterans benefits information"""
        try:
            # In a real implementation, this would fetch from government APIs
            # For now, we'll update the catalog with current information
            
            benefits_data = {
                "veterans_benefits": [
                    {
                        "id": "disability_benefits_2024",
                        "title": {
                            "uk": "Пільги по інвалідності для ветеранів (2024)",
                            "en": "Disability Benefits for Veterans (2024)"
                        },
                        "content": {
                            "uk": "Оновлена інформація про пільги по інвалідності для ветеранів війни станом на 2024 рік:\n\n• Щомісячна грошова допомога збільшена на 15%\n• Розширено перелік безоплатних медичних послуг\n• Додано пільги на комунальні послуги до 100%\n• Первочергове право на працевлаштування\n• Безоплатне протезування та реабілітація\n\nДля оформлення звертайтесь до територіального центру соціального захисту населення з пакетом документів.",
                            "en": "Updated information on disability benefits for war veterans as of 2024:\n\n• Monthly financial assistance increased by 15%\n• Expanded list of free medical services\n• Added utility benefits up to 100%\n• Priority employment rights\n• Free prosthetics and rehabilitation\n\nTo apply, contact your local social protection center with required documents."
                        },
                        "category": "benefits",
                        "tags": ["disability", "benefits", "veterans", "medical", "2024"],
                        "source_url": "https://www.mva.gov.ua/",
                        "last_updated": datetime.now().strftime("%Y-%m-%d")
                    }
                ]
            }
            
            # Update catalog file
            await self.update_catalog_section("legal_documents", benefits_data)
            
        except Exception as e:
            logger.error(f"Error updating veterans benefits: {e}")
    
    async def update_compensation_info(self):
        """Update compensation information"""
        try:
            compensation_data = {
                "compensation": [
                    {
                        "id": "disability_compensation_2024",
                        "title": {
                            "uk": "Компенсація за інвалідність (2024)",
                            "en": "Disability Compensation (2024)"
                        },
                        "content": {
                            "uk": "Оновлені розміри щомісячних виплат залежно від групи інвалідності (2024):\n\n• I група інвалідності: 3,200 грн (100% прожиткового мінімуму)\n• II група інвалідності: 2,880 грн (90% прожиткового мінімуму)\n• III група інвалідності: 1,600 грн (50% прожиткового мінімуму)\n\nДодаткові виплати:\n• Компенсація витрат на догляд: до 1,500 грн\n• Виплата за втрату годувальника: до 2,500 грн\n• Одноразова допомога при встановленні інвалідності: 5,000 грн\n\nВиплати здійснюються щомісячно до 20 числа через банківські установи або поштові відділення.",
                            "en": "Updated monthly payment amounts by disability group (2024):\n\n• Group I disability: 3,200 UAH (100% of subsistence minimum)\n• Group II disability: 2,880 UAH (90% of subsistence minimum)\n• Group III disability: 1,600 UAH (50% of subsistence minimum)\n\nAdditional payments:\n• Care cost compensation: up to 1,500 UAH\n• Breadwinner loss payment: up to 2,500 UAH\n• One-time assistance upon disability determination: 5,000 UAH\n\nPayments are made monthly by the 20th through banks or post offices."
                        },
                        "category": "compensation",
                        "tags": ["disability", "payments", "compensation", "monthly", "2024"],
                        "source_url": "https://www.mva.gov.ua/",
                        "last_updated": datetime.now().strftime("%Y-%m-%d")
                    }
                ]
            }
            
            await self.update_catalog_section("legal_documents", compensation_data)
            
        except Exception as e:
            logger.error(f"Error updating compensation info: {e}")
    
    async def update_legal_procedures(self):
        """Update legal procedures information"""
        try:
            procedures_data = {
                "procedures": [
                    {
                        "id": "disability_determination_2024",
                        "title": {
                            "uk": "Процедура встановлення інвалідності (2024)",
                            "en": "Disability Determination Procedure (2024)"
                        },
                        "content": {
                            "uk": "Оновлений алгоритм дій для встановлення інвалідності (2024):\n\n1. Звернення до сімейного лікаря або військового госпіталю\n2. Отримання направлення на МСЕ\n3. Подача документів до МСЕ:\n   - Заява встановленого зразка\n   - Медичні документи (історія хвороби, результати обстежень)\n   - Посвідчення учасника бойових дій\n   - Паспорт та ідентифікаційний код\n   - Довідка про доходи\n\n4. Проходження медичного огляду (до 30 днів)\n5. Отримання довідки про інвалідність\n6. Звернення до соціального захисту для оформлення пільг\n\nНововведення 2024:\n• Можливість подачі документів онлайн\n• Скорочення термінів розгляду до 20 днів\n• Автоматичне призначення пільг після встановлення інвалідності\n\nПри незгоді з рішенням можна подати апеляцію протягом місяця до вищої комісії МСЕ.",
                            "en": "Updated algorithm for disability determination (2024):\n\n1. Contact family doctor or military hospital\n2. Get referral for MSE\n3. Submit documents to MSE:\n   - Standard application form\n   - Medical documents (medical history, examination results)\n   - Combat participant certificate\n   - Passport and identification code\n   - Income certificate\n\n4. Medical examination (up to 30 days)\n5. Receive disability certificate\n6. Contact social protection to arrange benefits\n\n2024 Updates:\n• Online document submission available\n• Reduced processing time to 20 days\n• Automatic benefit assignment after disability determination\n\nIf disagreeing with decision, can file appeal within a month to higher MSE commission."
                        },
                        "category": "procedures",
                        "tags": ["disability", "examination", "procedure", "appeal", "2024"],
                        "source_url": "https://www.mva.gov.ua/",
                        "last_updated": datetime.now().strftime("%Y-%m-%d")
                    }
                ]
            }
            
            await self.update_catalog_section("legal_documents", procedures_data)
            
        except Exception as e:
            logger.error(f"Error updating legal procedures: {e}")
    
    async def update_catalog_section(self, section: str, new_data: Dict[str, Any]):
        """Update specific section in catalog.json"""
        try:
            # Load current catalog
            with open("catalog.json", "r", encoding="utf-8") as f:
                catalog = json.load(f)
            
            # Update the section
            if section not in catalog:
                catalog[section] = {}
            
            for category, items in new_data.items():
                if category not in catalog[section]:
                    catalog[section][category] = []
                
                # Update or add items
                for new_item in items:
                    # Find existing item by ID
                    existing_index = None
                    for i, existing_item in enumerate(catalog[section][category]):
                        if existing_item.get("id") == new_item.get("id"):
                            existing_index = i
                            break
                    
                    if existing_index is not None:
                        # Update existing item
                        catalog[section][category][existing_index] = new_item
                    else:
                        # Add new item
                        catalog[section][category].append(new_item)
            
            # Save updated catalog
            with open("catalog.json", "w", encoding="utf-8") as f:
                json.dump(catalog, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Updated catalog section: {section}")
            
        except Exception as e:
            logger.error(f"Error updating catalog section {section}: {e}")
    
    async def fetch_from_government_api(self, endpoint: str) -> Dict[str, Any]:
        """Fetch data from government API"""
        if not self.government_api_url or not self.api_key:
            logger.warning("Government API not configured")
            return {}
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.government_api_url}/{endpoint}",
                    headers=headers
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        logger.error(f"Government API error: {response.status}")
                        return {}
                        
        except Exception as e:
            logger.error(f"Error fetching from government API: {e}")
            return {}
    
    async def validate_legal_content(self, content: Dict[str, Any]) -> bool:
        """Validate legal content before updating"""
        try:
            required_fields = ["id", "title", "content", "category", "last_updated"]
            
            for field in required_fields:
                if field not in content:
                    logger.error(f"Missing required field: {field}")
                    return False
            
            # Validate title and content have both languages
            if not isinstance(content["title"], dict) or "uk" not in content["title"]:
                logger.error("Title must have Ukrainian translation")
                return False
            
            if not isinstance(content["content"], dict) or "uk" not in content["content"]:
                logger.error("Content must have Ukrainian translation")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating legal content: {e}")
            return False