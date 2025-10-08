#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
بوت تيليجرام لبيع البروكسيات
Simple Proxy Bot - Telegram Bot for Selling Proxies
"""

import os
import asyncio
import logging
import sqlite3
import json
import random
import string
import pandas as pd
import io
import csv
import openpyxl
import atexit
import platform
import subprocess
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import pytz
import re

# استيراد fcntl فقط في أنظمة Unix/Linux
try:
    import fcntl
    FCNTL_AVAILABLE = True
except ImportError:
    FCNTL_AVAILABLE = False

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    filters,
    ContextTypes
)
from telegram.constants import ParseMode

# تكوين اللوجينج
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# إضافة معالج للأخطاء العامة
import asyncio
import time
from typing import Dict, Set
from functools import wraps

# تم إزالة timeout handler لتحسين الأداء والاستقرار

# الإعدادات الثابتة - يتم تحميلها من متغيرات البيئة
ADMIN_PASSWORD = "sohilSOHIL"  # كلمة مرور الأدمن
TOKEN = "7751227560:AAHe4nZzMtI4JFJqx0HK84DiBfxztW5Y_jY"  # توكن البوت
DATABASE_FILE = "proxy_bot.db"
ACTIVE_ADMINS = []  # قائمة معرفات الآدمن النشطين المسجلين دخولهم حالياً
ADMIN_CHAT_ID = None  # معرف دردشة الأدمن - يتم تحميله من قاعدة البيانات

# حالات المحادثة
(
    ADMIN_LOGIN, ADMIN_MENU, PROCESS_ORDER, 
    ENTER_PROXY_TYPE, ENTER_PROXY_ADDRESS, ENTER_PROXY_PORT,
    ENTER_COUNTRY, ENTER_STATE, ENTER_USERNAME, ENTER_PASSWORD,
    ENTER_THANK_MESSAGE, PAYMENT_PROOF, CUSTOM_MESSAGE,
    REFERRAL_AMOUNT, USER_LOOKUP, QUIET_HOURS, LANGUAGE_SELECTION,
    PAYMENT_METHOD_SELECTION, WITHDRAWAL_REQUEST, SET_PRICE_STATIC,
    SET_PRICE_SOCKS, ADMIN_ORDER_INQUIRY, BROADCAST_MESSAGE,
    BROADCAST_USERS, BROADCAST_CONFIRM, PACKAGE_MESSAGE, PACKAGE_CONFIRMATION,
    PACKAGE_ACTION_CHOICE, SET_PRICE_RESIDENTIAL, SET_PRICE_ISP,
    SET_PRICE_ISP_ATT, SET_PRICE_VERIZON, SET_PRICE_RESIDENTIAL_2,
    SET_PRICE_DAILY, SET_PRICE_WEEKLY, ADD_FREE_PROXY, DELETE_FREE_PROXY,
    ENTER_PROXY_QUANTITY, EDIT_SERVICES_MESSAGE_AR, EDIT_SERVICES_MESSAGE_EN, 
    EDIT_EXCHANGE_RATE_MESSAGE_AR, EDIT_EXCHANGE_RATE_MESSAGE_EN,
    BALANCE_RECHARGE_REQUEST, BALANCE_RECHARGE_PROOF, SET_POINT_PRICE,
    ENTER_RECHARGE_AMOUNT, CONFIRM_DELETE_ALL_ORDERS, ADMIN_RECHARGE_AMOUNT_INPUT,
    # حالات جديدة لإدارة المستخدمين المتقدمة
    BAN_USER_CONFIRM, UNBAN_USER_CONFIRM, REMOVE_TEMP_BAN_CONFIRM,
    ADD_POINTS_AMOUNT, ADD_POINTS_MESSAGE, SUBTRACT_POINTS_AMOUNT, SUBTRACT_POINTS_MESSAGE,
    ADD_REFERRAL_USERNAME, DELETE_REFERRAL_SELECT, RESET_REFERRAL_CONFIRM,
    SINGLE_USER_BROADCAST_MESSAGE, MANAGE_USER_BANS

) = range(60)

# قواميس البيانات
STATIC_COUNTRIES = {
    'ar': {
        'US': '🇺🇸 الولايات المتحدة',
        'UK': '🇬🇧 بريطانيا',
        'FR': '🇫🇷 فرنسا',
        'DE': '🇩🇪 ألمانيا',
        'AT': '🇦🇹 النمسا'
    },
    'en': {
        'US': '🇺🇸 United States',
        'UK': '🇬🇧 United Kingdom',
        'FR': '🇫🇷 France',
        'DE': '🇩🇪 Germany',
        'AT': '🇦🇹 Austria'
    }
}

SOCKS_COUNTRIES = {
    'ar': {
        'US': '🇺🇸 الولايات المتحدة',
        'FR': '🇫🇷 فرنسا',
        'ES': '🇪🇸 إسبانيا',
        'UK': '🇬🇧 بريطانيا',
        'CA': '🇨🇦 كندا',
        'DE': '🇩🇪 ألمانيا',
        'IT': '🇮🇹 إيطاليا',
        'SE': '🇸🇪 السويد',
        'UA': '🇺🇦 أوكرانيا',
        'PL': '🇵🇱 بولندا',
        'NL': '🇳🇱 هولندا',
        'RO': '🇷🇴 رومانيا',
        'BG': '🇧🇬 بلغاريا',
        'RS': '🇷🇸 صربيا',
        'CZ': '🇨🇿 التشيك',
        'AE': '🇦🇪 الإمارات العربية المتحدة',
        'FI': '🇫🇮 فنلندا',
        'BE': '🇧🇪 بلجيكا',
        'HU': '🇭🇺 المجر',
        'PT': '🇵🇹 البرتغال',
        'GR': '🇬🇷 اليونان',
        'NO': '🇳🇴 النرويج',
        'AT': '🇦🇹 النمسا',
        'BY': '🇧🇾 بيلاروسيا',
        'SK': '🇸🇰 سلوفاكيا',
        'AL': '🇦🇱 ألبانيا',
        'MD': '🇲🇩 مولدوفا',
        'LT': '🇱🇹 ليتوانيا',
        'CH': '🇨🇭 سويسرا',
        'DK': '🇩🇰 الدنمارك',
        'IE': '🇮🇪 أيرلندا',
        'EE': '🇪🇪 إستونيا',
        'MT': '🇲🇹 مالطا',
        'LU': '🇱🇺 لوكسمبورغ',
        'CY': '🇨🇾 قبرص',
        'BA': '🇧🇦 البوسنة والهرسك',
        'SY': '🇸🇾 سوريا',
        'IS': '🇮🇸 أيسلندا',
        'MK': '🇲🇰 مقدونيا الشمالية'
    },
    'en': {
        'US': '🇺🇸 United States',
        'FR': '🇫🇷 France',
        'ES': '🇪🇸 Spain',
        'UK': '🇬🇧 United Kingdom',
        'CA': '🇨🇦 Canada',
        'DE': '🇩🇪 Germany',
        'IT': '🇮🇹 Italy',
        'SE': '🇸🇪 Sweden',
        'UA': '🇺🇦 Ukraine',
        'PL': '🇵🇱 Poland',
        'NL': '🇳🇱 Netherlands',
        'RO': '🇷🇴 Romania',
        'BG': '🇧🇬 Bulgaria',
        'RS': '🇷🇸 Serbia',
        'CZ': '🇨🇿 Czechia',
        'AE': '🇦🇪 United Arab Emirates',
        'FI': '🇫🇮 Finland',
        'BE': '🇧🇪 Belgium',
        'HU': '🇭🇺 Hungary',
        'PT': '🇵🇹 Portugal',
        'GR': '🇬🇷 Greece',
        'NO': '🇳🇴 Norway',
        'AT': '🇦🇹 Austria',
        'BY': '🇧🇾 Belarus',
        'SK': '🇸🇰 Slovakia',
        'AL': '🇦🇱 Albania',
        'MD': '🇲🇩 Moldova',
        'LT': '🇱🇹 Lithuania',
        'CH': '🇨🇭 Switzerland',
        'DK': '🇩🇰 Denmark',
        'IE': '🇮🇪 Ireland',
        'EE': '🇪🇪 Estonia',
        'MT': '🇲🇹 Malta',
        'LU': '🇱🇺 Luxembourg',
        'CY': '🇨🇾 Cyprus',
        'BA': '🇧🇦 Bosnia and Herzegovina',
        'SY': '🇸🇾 Syria',
        'IS': '🇮🇸 Iceland',
        'MK': '🇲🇰 North Macedonia'
    }
}

# ولايات السوكس (الكاملة)
US_STATES_SOCKS = {
    'ar': {
        'AL': 'ألاباما',
        'AK': 'ألاسكا', 
        'AZ': 'أريزونا',
        'AR': 'أركنساس',
        'CA': 'كاليفورنيا',
        'CO': 'كولورادو',
        'CT': 'كونيتيكت',
        'DE': 'ديلاوير',
        'FL': 'فلوريدا',
        'GA': 'جورجيا',
        'HI': 'هاواي',
        'ID': 'أيداهو',
        'IL': 'إلينوي',
        'IN': 'إنديانا',
        'IA': 'أيوا',
        'KS': 'كانساس',
        'KY': 'كنتاكي',
        'LA': 'لويزيانا',
        'ME': 'مين',
        'MD': 'ماريلاند',
        'MA': 'ماساتشوستس',
        'MI': 'ميشيغان',
        'MN': 'مينيسوتا',
        'MS': 'ميسيسيبي',
        'MO': 'ميزوري',
        'MT': 'مونتانا',
        'NE': 'نبراسكا',
        'NV': 'نيفادا',
        'NH': 'نيو هامبشير',
        'NJ': 'نيو جيرسي',
        'NM': 'نيو مكسيكو',
        'NY': 'نيويورك',
        'NC': 'كارولينا الشمالية',
        'ND': 'داكوتا الشمالية',
        'OH': 'أوهايو',
        'OK': 'أوكلاهوما',
        'OR': 'أوريغون',
        'PA': 'بنسلفانيا',
        'RI': 'رود آيلاند',
        'SC': 'كارولينا الجنوبية',
        'SD': 'داكوتا الجنوبية',
        'TN': 'تينيسي',
        'TX': 'تكساس',
        'UT': 'يوتا',
        'VT': 'فيرمونت',
        'VA': 'فيرجينيا',
        'WA': 'واشنطن',
        'WV': 'فيرجينيا الغربية',
        'WI': 'ويسكونسن',
        'WY': 'وايومنغ'
    },
    'en': {
        'AL': 'Alabama',
        'AK': 'Alaska',
        'AZ': 'Arizona',
        'AR': 'Arkansas',
        'CA': 'California',
        'CO': 'Colorado',
        'CT': 'Connecticut',
        'DE': 'Delaware',
        'FL': 'Florida',
        'GA': 'Georgia',
        'HI': 'Hawaii',
        'ID': 'Idaho',
        'IL': 'Illinois',
        'IN': 'Indiana',
        'IA': 'Iowa',
        'KS': 'Kansas',
        'KY': 'Kentucky',
        'LA': 'Louisiana',
        'ME': 'Maine',
        'MD': 'Maryland',
        'MA': 'Massachusetts',
        'MI': 'Michigan',
        'MN': 'Minnesota',
        'MS': 'Mississippi',
        'MO': 'Missouri',
        'MT': 'Montana',
        'NE': 'Nebraska',
        'NV': 'Nevada',
        'NH': 'New Hampshire',
        'NJ': 'New Jersey',
        'NM': 'New Mexico',
        'NY': 'New York',
        'NC': 'North Carolina',
        'ND': 'North Dakota',
        'OH': 'Ohio',
        'OK': 'Oklahoma',
        'OR': 'Oregon',
        'PA': 'Pennsylvania',
        'RI': 'Rhode Island',
        'SC': 'South Carolina',
        'SD': 'South Dakota',
        'TN': 'Tennessee',
        'TX': 'Texas',
        'UT': 'Utah',
        'VT': 'Vermont',
        'VA': 'Virginia',
        'WA': 'Washington',
        'WV': 'West Virginia',
        'WI': 'Wisconsin',
        'WY': 'Wyoming'
    }
}

# ولايات الستاتيك الريزيدنتال الشهري - $6
US_STATES_STATIC_RESIDENTIAL = {
    'ar': {
        'NY': 'نيويورك',
        'AZ': 'أريزونا',
        'DE': 'ديلاوير',
        'VA': 'فيرجينيا'
    },
    'en': {
        'NY': 'New York',
        'AZ': 'Arizona',
        'DE': 'Delaware',
        'VA': 'Virginia'
    }
}

# ولايات الستاتيك Verizon ريزيدنتال الشهري - $4
US_STATES_STATIC_VERIZON = {
    'ar': {
        'NY': 'نيويورك',
        'VA': 'فيرجينيا',
        'WA': 'واشنطن'
    },
    'en': {
        'NY': 'New York',
        'VA': 'Virginia',
        'WA': 'Washington'
    }
}

# ولايات الستاتيك Crocker ريزيدنتال الشهري - $4
US_STATES_STATIC_CROCKER = {
    'ar': {
        'MA': 'ماساتشوستس'
    },
    'en': {
        'MA': 'Massachusetts'
    }
}

# ولايات الستاتيك الأسبوعي - $2.5
STATIC_WEEKLY_LOCATIONS = {
    'ar': {
        'US': {
            'NY': 'نيويورك',
            'VA': 'فيرجينيا',
            'WA': 'واشنطن'
        }
    },
    'en': {
        'US': {
            'NY': 'New York',
            'VA': 'Virginia', 
            'WA': 'Washington'
        }
    }
}

# ولايات الستاتيك ISP (خيار واحد فقط)
# ولايات أمريكا للستاتيك الريزيدنتال
US_STATES_STATIC_RESIDENTIAL = {
    'ar': {
        'NY': 'نيويورك',
        'AZ': 'أريزونا', 
        'DE': 'ديلاوير',
        'VA': 'فيرجينيا',
        'WA': 'واشنطن'
    },
    'en': {
        'NY': 'New York',
        'AZ': 'Arizona',
        'DE': 'Delaware', 
        'VA': 'Virginia',
        'WA': 'Washington'
    }
}

# ستاتيك ISP
US_STATES_STATIC_ISP = {
    'ar': {
        'ATT': 'ISP (عشوائي الموقع)'
    },
    'en': {
        'ATT': 'ISP (Random Location)'
    }
}

# للبحث السريع - backward compatibility
US_STATES = US_STATES_SOCKS

UK_STATES = {
    'ar': {
        'ENG': 'إنجلترا',
        'SCT': 'اسكتلندا',
        'WAL': 'ويلز',
        'NIR': 'أيرلندا الشمالية'
    },
    'en': {
        'ENG': 'England',
        'SCT': 'Scotland',
        'WAL': 'Wales', 
        'NIR': 'Northern Ireland'
    }
}

# مناطق ألمانيا
DE_STATES = {
    'ar': {
        'BW': 'بادن فورتمبيرغ',
        'BY': 'بافاريا',
        'BE': 'برلين',
        'BB': 'براندنبورغ',
        'HB': 'بريمن',
        'HH': 'هامبورغ',
        'HE': 'هيسن',
        'NI': 'ساكسونيا السفلى',
        'NW': 'شمال الراين وستفاليا',
        'RP': 'راينلاند بالاتينات',
        'SL': 'سارلاند',
        'SN': 'ساكسونيا',
        'ST': 'ساكسونيا أنهالت',
        'SH': 'شليسفيغ هولشتاين',
        'TH': 'تورينغن'
    },
    'en': {
        'BW': 'Baden-Württemberg',
        'BY': 'Bavaria',
        'BE': 'Berlin',
        'BB': 'Brandenburg',
        'HB': 'Bremen',
        'HH': 'Hamburg',
        'HE': 'Hesse',
        'NI': 'Lower Saxony',
        'NW': 'North Rhine-Westphalia',
        'RP': 'Rhineland-Palatinate',
        'SL': 'Saarland',
        'SN': 'Saxony',
        'ST': 'Saxony-Anhalt',
        'SH': 'Schleswig-Holstein',
        'TH': 'Thuringia'
    }
}

# مناطق فرنسا
FR_STATES = {
    'ar': {
        'ARA': 'أوفيرن رون ألب',
        'BFC': 'بورغونيا فرانش كونته',
        'BRE': 'بريتاني',
        'CVL': 'وسط وادي اللوار',
        'COR': 'كورسيكا',
        'GES': 'الألزاس الشرقي',
        'HDF': 'هو دو فرانس',
        'IDF': 'إيل دو فرانس',
        'NOR': 'نورماندي',
        'NAQ': 'آكيتين الجديدة',
        'OCC': 'أوكسيتانيا',
        'PDL': 'باي دو لا لوار',
        'PAC': 'بروفانس ألب كوت دازور'
    },
    'en': {
        'ARA': 'Auvergne-Rhône-Alpes',
        'BFC': 'Burgundy-Franche-Comté',
        'BRE': 'Brittany',
        'CVL': 'Centre-Val de Loire',
        'COR': 'Corsica',
        'GES': 'Grand Est',
        'HDF': 'Hauts-de-France',
        'IDF': 'Île-de-France',
        'NOR': 'Normandy',
        'NAQ': 'Nouvelle-Aquitaine',
        'OCC': 'Occitania',
        'PDL': 'Pays de la Loire',
        'PAC': 'Provence-Alpes-Côte d\'Azur'
    }
}

# مناطق إيطاليا
IT_STATES = {
    'ar': {
        'ABR': 'أبروتسو',
        'BAS': 'باسيليكاتا',
        'CAL': 'كالابريا',
        'CAM': 'كامبانيا',
        'EMR': 'إميليا رومانيا',
        'FVG': 'فريولي فينيتسيا جوليا',
        'LAZ': 'لاتسيو',
        'LIG': 'ليغوريا',
        'LOM': 'لومبارديا',
        'MAR': 'ماركي',
        'MOL': 'موليسي',
        'PIE': 'بيدمونت',
        'PUG': 'بوليا',
        'SAR': 'سردينيا',
        'SIC': 'صقلية',
        'TOS': 'توسكانا',
        'TRE': 'ترينتينو ألتو أديجي',
        'UMB': 'أومبريا',
        'VDA': 'وادي أوستا',
        'VEN': 'فينيتو'
    },
    'en': {
        'ABR': 'Abruzzo',
        'BAS': 'Basilicata',
        'CAL': 'Calabria',
        'CAM': 'Campania',
        'EMR': 'Emilia-Romagna',
        'FVG': 'Friuli-Venezia Giulia',
        'LAZ': 'Lazio',
        'LIG': 'Liguria',
        'LOM': 'Lombardy',
        'MAR': 'Marche',
        'MOL': 'Molise',
        'PIE': 'Piedmont',
        'PUG': 'Puglia',
        'SAR': 'Sardinia',
        'SIC': 'Sicily',
        'TOS': 'Tuscany',
        'TRE': 'Trentino-Alto Adige',
        'UMB': 'Umbria',
        'VDA': 'Aosta Valley',
        'VEN': 'Veneto'
    }
}

# مناطق إسبانيا
ES_STATES = {
    'ar': {
        'AND': 'الأندلس',
        'ARA': 'أراغون',
        'AST': 'أستورياس',
        'BAL': 'جزر البليار',
        'PV': 'الباسك',
        'CAN': 'جزر الكناري',
        'CAB': 'كانتابريا',
        'CLM': 'قشتالة لا مانتشا',
        'CYL': 'قشتالة وليون',
        'CAT': 'كاتالونيا',
        'EXT': 'إكستريمادورا',
        'GAL': 'غاليسيا',
        'MAD': 'مدريد',
        'MUR': 'مورسيا',
        'NAV': 'نافارا',
        'RIO': 'لا ريوخا',
        'VAL': 'فالنسيا'
    },
    'en': {
        'AND': 'Andalusia',
        'ARA': 'Aragon',
        'AST': 'Asturias',
        'BAL': 'Balearic Islands',
        'PV': 'Basque Country',
        'CAN': 'Canary Islands',
        'CAB': 'Cantabria',
        'CLM': 'Castile-La Mancha',
        'CYL': 'Castile and León',
        'CAT': 'Catalonia',
        'EXT': 'Extremadura',
        'GAL': 'Galicia',
        'MAD': 'Madrid',
        'MUR': 'Murcia',
        'NAV': 'Navarre',
        'RIO': 'La Rioja',
        'VAL': 'Valencia'
    }
}

# مناطق كندا
CA_STATES = {
    'ar': {
        'AB': 'ألبرتا',
        'BC': 'كولومبيا البريطانية',
        'MB': 'مانيتوبا',
        'NB': 'نيو برونزويك',
        'NL': 'نيوفاوندلاند ولابرادور',
        'NS': 'نوفا سكوتيا',
        'ON': 'أونتاريو',
        'PE': 'جزيرة الأمير إدوارد',
        'QC': 'كيبيك',
        'SK': 'ساسكاتشوان',
        'NT': 'الأقاليم الشمالية الغربية',
        'NU': 'نونافوت',
        'YT': 'يوكون'
    },
    'en': {
        'AB': 'Alberta',
        'BC': 'British Columbia',
        'MB': 'Manitoba',
        'NB': 'New Brunswick',
        'NL': 'Newfoundland and Labrador',
        'NS': 'Nova Scotia',
        'ON': 'Ontario',
        'PE': 'Prince Edward Island',
        'QC': 'Quebec',
        'SK': 'Saskatchewan',
        'NT': 'Northwest Territories',
        'NU': 'Nunavut',
        'YT': 'Yukon'
    }
}

# ولايات أستراليا
AU_STATES = {
    'ar': {
        'NSW': 'نيو ساوث ويلز',
        'VIC': 'فيكتوريا',
        'QLD': 'كوينزلاند',
        'SA': 'جنوب أستراليا',
        'WA': 'غرب أستراليا',
        'TAS': 'تاسمانيا',
        'NT': 'الإقليم الشمالي',
        'ACT': 'إقليم العاصمة الأسترالية'
    },
    'en': {
        'NSW': 'New South Wales',
        'VIC': 'Victoria',
        'QLD': 'Queensland',
        'SA': 'South Australia',
        'WA': 'Western Australia',
        'TAS': 'Tasmania',
        'NT': 'Northern Territory',
        'ACT': 'Australian Capital Territory'
    }
}

# ولايات النمسا
AT_STATES = {
    'ar': {
        'WIEN': 'فيينا',
        'NOE': 'النمسا السفلى',
        'OOE': 'النمسا العليا',
        'STMK': 'شتايرمارك',
        'KTN': 'كارينثيا',
        'SBG': 'سالزبورغ',
        'TIROL': 'تيرول',
        'VBG': 'فورآرلبرغ',
        'BGLD': 'بورغنلاند'
    },
    'en': {
        'WIEN': 'Vienna',
        'NOE': 'Lower Austria',
        'OOE': 'Upper Austria',
        'STMK': 'Styria',
        'KTN': 'Carinthia',
        'SBG': 'Salzburg',
        'TIROL': 'Tyrol',
        'VBG': 'Vorarlberg',
        'BGLD': 'Burgenland'
    }
}

# مناطق إيطاليا
IT_STATES = {
    'ar': {
        'LAZ': 'لاتسيو (روما)',
        'LOM': 'لومبارديا (ميلان)',
        'CAM': 'كامبانيا (نابولي)',
        'SIC': 'صقلية (باليرمو)',
        'VEN': 'فينيتو (فينيسيا)',
        'PIE': 'بيدمونت (تورين)',
        'PUG': 'بوليا (باري)',
        'EMR': 'إميليا رومانيا (بولونيا)',
        'TOS': 'توسكانا (فلورنسا)',
        'CAL': 'كالابريا',
        'SAR': 'سردينيا',
        'LIG': 'ليغوريا (جنوة)',
        'MAR': 'ماركي',
        'ABR': 'أبروتسو',
        'FVG': 'فريولي فينيتسيا جوليا',
        'TRE': 'ترينتينو ألتو أديجي',
        'UMB': 'أومبريا',
        'BAS': 'باسيليكاتا',
        'MOL': 'موليزي',
        'VAL': 'فالي داوستا'
    },
    'en': {
        'LAZ': 'Lazio (Rome)',
        'LOM': 'Lombardy (Milan)',
        'CAM': 'Campania (Naples)',
        'SIC': 'Sicily (Palermo)',
        'VEN': 'Veneto (Venice)',
        'PIE': 'Piedmont (Turin)',
        'PUG': 'Apulia (Bari)',
        'EMR': 'Emilia-Romagna (Bologna)',
        'TOS': 'Tuscany (Florence)',
        'CAL': 'Calabria',
        'SAR': 'Sardinia',
        'LIG': 'Liguria (Genoa)',
        'MAR': 'Marche',
        'ABR': 'Abruzzo',
        'FVG': 'Friuli-Venezia Giulia',
        'TRE': 'Trentino-Alto Adige',
        'UMB': 'Umbria',
        'BAS': 'Basilicata',
        'MOL': 'Molise',
        'VAL': 'Aosta Valley'
    }
}

# مقاطعات إسبانيا
ES_STATES = {
    'ar': {
        'MAD': 'مدريد',
        'CAT': 'كاتالونيا (برشلونة)',
        'AND': 'أندلسيا (إشبيلية)',
        'VAL': 'فالنسيا',
        'GAL': 'جاليسيا',
        'CAS': 'قشتالة وليون',
        'EUS': 'إقليم الباسك (بيلباو)',
        'CAN': 'جزر الكناري',
        'CLM': 'قشتالة لا مانشا',
        'MUR': 'مورسيا',
        'ARA': 'أراغون',
        'EXT': 'إكستريمادورا',
        'AST': 'أستورياس',
        'NAV': 'نافارا',
        'CAN_': 'كانتابريا',
        'BAL': 'جزر البليار',
        'RIO': 'لا ريوخا',
        'CEU': 'سبتة',
        'MEL': 'مليلية'
    },
    'en': {
        'MAD': 'Madrid',
        'CAT': 'Catalonia (Barcelona)',
        'AND': 'Andalusia (Seville)',
        'VAL': 'Valencia',
        'GAL': 'Galicia',
        'CAS': 'Castile and León',
        'EUS': 'Basque Country (Bilbao)',
        'CAN': 'Canary Islands',
        'CLM': 'Castilla-La Mancha',
        'MUR': 'Murcia',
        'ARA': 'Aragon',
        'EXT': 'Extremadura',
        'AST': 'Asturias',
        'NAV': 'Navarre',
        'CAN_': 'Cantabria',
        'BAL': 'Balearic Islands',
        'RIO': 'La Rioja',
        'CEU': 'Ceuta',
        'MEL': 'Melilla'
    }
}

# مقاطعات هولندا
NL_STATES = {
    'ar': {
        'NH': 'شمال هولندا (أمستردام)',
        'ZH': 'جنوب هولندا (لاهاي)',
        'NB': 'شمال برابانت',
        'UT': 'أوترخت',
        'GE': 'خيلدرلاند',
        'OV': 'أوفريجسل',
        'LI': 'ليمبورغ',
        'FR': 'فريزلاند',
        'GR': 'خرونينغن',
        'DR': 'درينت',
        'FL': 'فليفولاند',
        'ZE': 'زيلاند'
    },
    'en': {
        'NH': 'North Holland (Amsterdam)',
        'ZH': 'South Holland (The Hague)',
        'NB': 'North Brabant',
        'UT': 'Utrecht',
        'GE': 'Gelderland',
        'OV': 'Overijssel',
        'LI': 'Limburg',
        'FR': 'Friesland',
        'GR': 'Groningen',
        'DR': 'Drenthe',
        'FL': 'Flevoland',
        'ZE': 'Zeeland'
    }
}

# مقاطعات بلجيكا
BE_STATES = {
    'ar': {
        'BRU': 'بروكسل العاصمة',
        'VLG': 'فلاندرز',
        'WAL': 'والونيا',
        'ANT': 'أنتويرب',
        'LIM': 'ليمبورغ',
        'OVL': 'فلاندرز الشرقية',
        'WVL': 'فلاندرز الغربية',
        'VBR': 'فلامس برابانت',
        'HAI': 'هينو',
        'LIE': 'لييج',
        'LUX': 'لوكسمبورغ البلجيكية',
        'NAM': 'نامور',
        'WBR': 'والون برابانت'
    },
    'en': {
        'BRU': 'Brussels Capital',
        'VLG': 'Flanders',
        'WAL': 'Wallonia',
        'ANT': 'Antwerp',
        'LIM': 'Limburg',
        'OVL': 'East Flanders',
        'WVL': 'West Flanders',
        'VBR': 'Flemish Brabant',
        'HAI': 'Hainaut',
        'LIE': 'Liège',
        'LUX': 'Luxembourg (Belgium)',
        'NAM': 'Namur',
        'WBR': 'Walloon Brabant'
    }
}

# أقاليم سويسرا
CH_STATES = {
    'ar': {
        'ZH': 'زيورخ',
        'BE': 'برن',
        'LU': 'لوسيرن',
        'UR': 'أوري',
        'SZ': 'شفيتس',
        'OW': 'أوبفالدن',
        'NW': 'نيدفالدن',
        'GL': 'غلاريس',
        'ZG': 'تسوغ',
        'FR': 'فريبورغ',
        'SO': 'سولوتورن',
        'BS': 'بازل المدينة',
        'BL': 'بازل الريف',
        'SH': 'شافهاوزن',
        'AR': 'أبنزل الخارجية',
        'AI': 'أبنزل الداخلية',
        'SG': 'سانت غالن',
        'GR': 'غراوبوندن',
        'AG': 'أرغاو',
        'TG': 'تورغاو',
        'TI': 'تيتشينو',
        'VD': 'فو',
        'VS': 'فاليه',
        'NE': 'نوشاتيل',
        'GE': 'جنيف',
        'JU': 'جورا'
    },
    'en': {
        'ZH': 'Zurich',
        'BE': 'Bern',
        'LU': 'Lucerne',
        'UR': 'Uri',
        'SZ': 'Schwyz',
        'OW': 'Obwalden',
        'NW': 'Nidwalden',
        'GL': 'Glarus',
        'ZG': 'Zug',
        'FR': 'Fribourg',
        'SO': 'Solothurn',
        'BS': 'Basel-Stadt',
        'BL': 'Basel-Landschaft',
        'SH': 'Schaffhausen',
        'AR': 'Appenzell Ausserrhoden',
        'AI': 'Appenzell Innerrhoden',
        'SG': 'St. Gallen',
        'GR': 'Graubünden',
        'AG': 'Aargau',
        'TG': 'Thurgau',
        'TI': 'Ticino',
        'VD': 'Vaud',
        'VS': 'Valais',
        'NE': 'Neuchâtel',
        'GE': 'Geneva',
        'JU': 'Jura'
    }
}

# ولايات روسيا (أهم المناطق)
RU_STATES = {
    'ar': {
        'MOW': 'موسكو',
        'SPE': 'سان بطرسبرغ',
        'NSO': 'نوفوسيبيرسك',
        'EKB': 'يكاترينبورغ',
        'NIZ': 'نيجني نوفغورود',
        'KZN': 'قازان',
        'CHE': 'تشيليابينسك',
        'OMS': 'أومسك',
        'SAM': 'سامارا',
        'ROS': 'روستوف على الدون',
        'UFA': 'أوفا',
        'KRA': 'كراسنويارسك',
        'PER': 'بيرم',
        'VOR': 'فورونيج',
        'VOL': 'فولغوغراد'
    },
    'en': {
        'MOW': 'Moscow',
        'SPE': 'Saint Petersburg',
        'NSO': 'Novosibirsk',
        'EKB': 'Yekaterinburg',
        'NIZ': 'Nizhny Novgorod',
        'KZN': 'Kazan',
        'CHE': 'Chelyabinsk',
        'OMS': 'Omsk',
        'SAM': 'Samara',
        'ROS': 'Rostov-on-Don',
        'UFA': 'Ufa',
        'KRA': 'Krasnoyarsk',
        'PER': 'Perm',
        'VOR': 'Voronezh',
        'VOL': 'Volgograd'
    }
}

# محافظات اليابان (أهم المناطق)
JP_STATES = {
    'ar': {
        'TOK': 'طوكيو',
        'OSA': 'أوساكا',
        'KAN': 'كاناغاوا (يوكوهاما)',
        'AIC': 'آيتشي (ناغويا)',
        'SAI': 'سايتاما',
        'CHI': 'تشيبا',
        'HYO': 'هيوغو (كوبي)',
        'HOK': 'هوكايدو (سابورو)',
        'FUK': 'فوكوكا',
        'SHI': 'شيزوكا',
        'HIR': 'هيروشيما',
        'SEN': 'سينداي',
        'KYO': 'كيوتو',
        'NII': 'نيغاتا',
        'OKI': 'أوكيناوا'
    },
    'en': {
        'TOK': 'Tokyo',
        'OSA': 'Osaka',
        'KAN': 'Kanagawa (Yokohama)',
        'AIC': 'Aichi (Nagoya)',
        'SAI': 'Saitama',
        'CHI': 'Chiba',
        'HYO': 'Hyogo (Kobe)',
        'HOK': 'Hokkaido (Sapporo)',
        'FUK': 'Fukuoka',
        'SHI': 'Shizuoka',
        'HIR': 'Hiroshima',
        'SEN': 'Sendai',
        'KYO': 'Kyoto',
        'NII': 'Niigata',
        'OKI': 'Okinawa'
    }
}

# ولايات البرازيل (أهم المناطق)
BR_STATES = {
    'ar': {
        'SP': 'ساو باولو',
        'RJ': 'ريو دي جانيرو',
        'MG': 'ميناس جيرايس',
        'BA': 'باهيا',
        'PR': 'بارانا',
        'RS': 'ريو غراندي دو سول',
        'PE': 'بيرنامبوكو',
        'CE': 'سيارا',
        'PA': 'بارا',
        'SC': 'سانتا كاتارينا',
        'GO': 'غوياس',
        'PB': 'بارايبا',
        'MA': 'مارانهاو',
        'ES': 'إسبيريتو سانتو',
        'DF': 'المقاطعة الاتحادية (برازيليا)'
    },
    'en': {
        'SP': 'São Paulo',
        'RJ': 'Rio de Janeiro',
        'MG': 'Minas Gerais',
        'BA': 'Bahia',
        'PR': 'Paraná',
        'RS': 'Rio Grande do Sul',
        'PE': 'Pernambuco',
        'CE': 'Ceará',
        'PA': 'Pará',
        'SC': 'Santa Catarina',
        'GO': 'Goiás',
        'PB': 'Paraíba',
        'MA': 'Maranhão',
        'ES': 'Espírito Santo',
        'DF': 'Federal District (Brasília)'
    }
}

# ولايات المكسيك (أهم المناطق)
MX_STATES = {
    'ar': {
        'MX': 'مكسيكو سيتي',
        'JAL': 'خاليسكو (غوادالاخارا)',
        'NL': 'نويفو ليون (مونتيري)',
        'PUE': 'بوبلا',
        'GTO': 'غواناخواتو',
        'VER': 'فيراكروز',
        'YUC': 'يوكاتان',
        'BC': 'باجا كاليفورنيا',
        'CHIH': 'تشيهواهوا',
        'SON': 'سونورا',
        'COA': 'كواهويلا',
        'TAM': 'تاماوليباس',
        'SIN': 'سينالوا',
        'OAX': 'أواكساكا',
        'QRO': 'كيريتارو'
    },
    'en': {
        'MX': 'Mexico City',
        'JAL': 'Jalisco (Guadalajara)',
        'NL': 'Nuevo León (Monterrey)',
        'PUE': 'Puebla',
        'GTO': 'Guanajuato',
        'VER': 'Veracruz',
        'YUC': 'Yucatán',
        'BC': 'Baja California',
        'CHIH': 'Chihuahua',
        'SON': 'Sonora',
        'COA': 'Coahuila',
        'TAM': 'Tamaulipas',
        'SIN': 'Sinaloa',
        'OAX': 'Oaxaca',
        'QRO': 'Querétaro'
    }
}

# ولايات الهند (أهم المناطق)
IN_STATES = {
    'ar': {
        'DL': 'دلهي',
        'MH': 'ماهاراشترا (مومباي)',
        'KA': 'كارناتاكا (بنغالور)',
        'TN': 'تاميل نادو (تشيناي)',
        'WB': 'البنغال الغربية (كولكاتا)',
        'GJ': 'غوجارات',
        'RJ': 'راجاستان',
        'UP': 'أوتار براديش',
        'TG': 'تيلانغانا (حيدر أباد)',
        'AP': 'أندرا براديش',
        'KL': 'كيرالا',
        'OR': 'أوديشا',
        'JH': 'جهارخاند',
        'AS': 'آسام',
        'PB': 'البنجاب'
    },
    'en': {
        'DL': 'Delhi',
        'MH': 'Maharashtra (Mumbai)',
        'KA': 'Karnataka (Bangalore)',
        'TN': 'Tamil Nadu (Chennai)',
        'WB': 'West Bengal (Kolkata)',
        'GJ': 'Gujarat',
        'RJ': 'Rajasthan',
        'UP': 'Uttar Pradesh',
        'TG': 'Telangana (Hyderabad)',
        'AP': 'Andhra Pradesh',
        'KL': 'Kerala',
        'OR': 'Odisha',
        'JH': 'Jharkhand',
        'AS': 'Assam',
        'PB': 'Punjab'
    }
}

# رسائل النظام
MESSAGES = {
    'ar': {
        'welcome': """✨ ━━━━━━━━━━━━━━━ ✨

🌟 مرحباً بك في Static_Bot 🌟

✨ ━━━━━━━━━━━━━━━ ✨

💎 أفضل خدمات البروكسي الاحترافية 💎

🚀 اختر الخدمة المطلوبة من الأزرار أدناه:""",
        'static_package': """📦 باكج البروكسي الستاتيك

🔹 الأسعار المتوفرة:
• Static ISP: {isp_price}$
• Static Residential: {res_price}$
• Static Daily: {daily_price}$
• Static Weekly: {weekly_price}$

━━━━━━━━━━━━━━━
📋 بعد اختيار الخدمة:
✅ سيستقبل الأدمن طلبك
⚡ سنعالج الطلب ونرسل لك البروكسي
📬 ستصلك رسالة تأكيد عند الانتهاء

معرف الطلب: {order_id}""",
        'socks_package': """📦 باكج البروكسي السوكس
🌍 جميع دول العالم | اختيار الولاية والمزود

🔹 الأسعار المتوفرة:
• بروكسي واحد: {single_price}$
• بروكسيان اثنان: {double_price}$  
• باكج 5 بروكسيات مؤقتة: {five_price}$
• باكج 10 بروكسيات مؤقتة: {ten_price}$

━━━━━━━━━━━━━━━
📋 بعد اختيار الخدمة:
✅ سيستقبل الأدمن طلبك
⚡ سنعالج الطلب ونرسل لك البروكسي
📬 ستصلك رسالة تأكيد عند الانتهاء

معرف الطلب: {order_id}""",
        'select_country': 'اختر الدولة:',
        'select_state': 'اختر الولاية:',
        'payment_methods': 'اختر طريقة الدفع:',
        'send_payment_proof': 'يرجى إرسال إثبات الدفع (صورة فقط):',
        'order_received': '✅ تم استلام طلبك بنجاح!\n\n📋 سيتم معالجة الطلب يدوياً من الأدمن بأقرب وقت.\n\n📧 ستصلك تحديثات الحالة تلقائياً.',
        'main_menu_buttons': ['🔒 طلب بروكسي ستاتيك', '📡 طلب بروكسي سوكس مؤقت', '🎁 تجربة ستاتيك مجانا', '💰 الرصيد', '📋 تذكير بطلباتي', '⚙️ الإعدادات', '🛠️ المزيد من الخدمات'],
        'admin_main_buttons': ['📋 إدارة الطلبات', '💰 إدارة الأموال', '👥 الإحالات', '📢 البث', '⚙️ الإعدادات'],
        'change_password': 'تغيير كلمة المرور',
        'password_changed': 'تم تغيير كلمة المرور بنجاح ✅',
        'invalid_password': 'كلمة المرور غير صحيحة!',
        'enter_new_password': 'يرجى إدخال كلمة المرور الجديدة:',
        'withdrawal_processing': 'جاري معالجة طلب سحب رصيدك من قبل الأدمن...',
        'admin_contact': 'ستتواصل الإدارة معك قريباً لتسليمك مكافأتك.',
        'language_change_success': 'تم تغيير اللغة إلى العربية ✅\nيرجى استخدام الأمر /start لإعادة تحميل القوائم',
        'admin_panel': '🔧 لوحة الأدمن',
        'manage_orders': 'إدارة الطلبات',
        'pending_orders': 'الطلبات المعلقة',
        'admin_login_prompt': 'يرجى إدخال كلمة المرور:',
        'order_processing': '⚙️ جاري معالجة طلبك الآن من قبل الأدمن...',
        'order_success': '✅ تم إنجاز طلبك بنجاح! تم إرسال تفاصيل البروكسي إليك.',
        'order_failed': '❌ تم رفض طلبك. يرجى التحقق من إثبات الدفع والمحاولة مرة أخرى.',
        'about_bot': """🤖 حول البوت

📦 بوت بيع البروكسي وإدارة البروكسي
🔢 الإصدار: 1.0.0

━━━━━━━━━━━━━━━
🧑‍💻 طُور بواسطة: Mohamad Zalaf

📞 معلومات الاتصال:
📱 تليجرام: @MohamadZalaf
📧 البريد الإلكتروني: 
   • MohamadZalaf@outlook.com
   • Mohamadzalaf2017@gmail.com

━━━━━━━━━━━━━━━
© Mohamad Zalaf 2025""",
        'proxy_quantity': '🔢 أدخل عدد البروكسيات المطلوبة\n\n📝 يجب أن يكون رقماً صحيحاً بين 1 و 99\n\nمثال: 5',
        'invalid_quantity': '❌ عدد غير صحيح!\n\n🔢 يرجى إدخال رقم صحيح بين 1 و 99 فقط\n❌ لا تستخدم فواصل أو نصوص\n\nمثال صحيح: 5\nمثال خاطئ: 2.5 أو خمسة',
        'services_info': 'هذه رسالة الخدمات الافتراضية. يمكن للإدارة تعديلها.',
        
        # رسائل نظام الرصيد
        'balance_menu_buttons': ['💳 شحن رصيد', '💰 رصيدي', '👥 الإحالات', '↩️ العودة للقائمة الرئيسية'],
        'balance_menu_title': '💰 إدارة الرصيد\n\nاختر العملية المطلوبة:',
        'current_balance': '''💰 رصيدك الحالي:
        
━━━━━━━━━━━━━━━
💳 رصيد الشحن: {charged_balance:.2f} كريديت
👥 رصيد الإحالات: {referral_balance:.2f} كريديت
━━━━━━━━━━━━━━━
🔢 الرصيد الإجمالي: {total_balance:.2f} كريديت''',
        'recharge_request': '''💳 طلب شحن رصيد
        
💎 قيمة الكريديت الواحد: ${credit_price:.2f}

اختر طريقة الدفع للمتابعة:''',
        'enter_recharge_amount': '💎 أدخل قيمة المبلغ المراد شحنه بالدولار:\n\nمثال: 10',
        'invalid_recharge_amount': '❌ قيمة غير صحيحة! يرجى إدخال رقم صحيح أكبر من 0',
        'recharge_proof_request': 'يرجى إرسال إثبات الدفع (صورة فقط):',
        'recharge_order_created': '✅ تم إنشاء طلب شحن الرصيد بنجاح!\n\n🆔 معرف الطلب: {order_id}\n💰 المبلغ: ${amount:.2f}\n💎 الكريديت المتوقع: {points:.2f} كريديت\n\n📋 سيتم مراجعة الطلب من قبل الأدمن'
    },
    'en': {
        'welcome': """✨ ━━━━━━━━━━━━━━━ ✨

🌟 Welcome to Static_Bot 🌟

✨ ━━━━━━━━━━━━━━━ ✨

💎 Premium Proxy Services 💎

🚀 Choose the required service from the buttons below:""",
        'static_package': """📦 Static Proxy Package

🔹 Available Prices:
• Static ISP: {isp_price}$
• Static Residential: {res_price}$
• Static Daily: {daily_price}$
• Static Weekly: {weekly_price}$

━━━━━━━━━━━━━━━
📋 After selecting service:
✅ Admin will receive your order
⚡ We'll process and send you the proxy
📬 You'll get confirmation when ready

Order ID will be generated""",
        'socks_package': """📦 Socks Proxy Package
🌍 Worldwide | Choose State & Provider

🔹 Available Prices:
• One Proxy: {single_price}$
• Two Proxies: {double_price}$
• 5 Temporary Proxies Package: {five_price}$
• 10 Temporary Proxies Package: {ten_price}$

━━━━━━━━━━━━━━━
📋 After selecting service:
✅ Admin will receive your order
⚡ We'll process and send you the proxy
📬 You'll get confirmation when ready

Order ID: {order_id}""",
        'select_country': 'Select Country:',
        'select_state': 'Select State:',
        'payment_methods': 'Choose payment method:',
        'send_payment_proof': 'Please send payment proof (image only):',
        'order_received': '✅ Your order has been received successfully!\n\n📋 Admin will process it manually soon.\n\n📧 You will receive status updates automatically.',
        'main_menu_buttons': ['🔒 Request Static Proxy', '📡 Request Temporary Socks Proxy', '🎁 Free Static Trial', '💰 Balance', '📋 Order Reminder', '⚙️ Settings', '🛠️ Our Services'],
        'admin_main_buttons': ['📋 Manage Orders', '💰 Manage Money', '👥 Referrals', '📢 Broadcast', '⚙️ Settings'],
        'change_password': 'Change Password',
        'password_changed': 'Password changed successfully ✅',
        'invalid_password': 'Invalid password!',
        'enter_new_password': 'Please enter new password:',
        'withdrawal_processing': 'Your withdrawal request is being processed by admin...',
        'admin_contact': 'Admin will contact you soon to deliver your reward.',
        'language_change_success': 'Language changed to English ✅\nPlease use /start command to reload menus',
        'admin_panel': '🔧 Admin Panel',
        'manage_orders': 'Manage Orders',
        'pending_orders': 'Pending Orders',
        'admin_login_prompt': 'Please enter password:',
        'order_processing': '⚙️ Your order is now being processed by admin...',
        'order_success': '✅ Your order has been completed successfully! Proxy details have been sent to you.',
        'order_failed': '❌ Your order has been rejected. Please check your payment proof and try again.',
        'about_bot': """🤖 About Bot

📦 Proxy Sales & Management Bot
🔢 Version: 1.0.0

━━━━━━━━━━━━━━━
🧑‍💻 Developed by: Mohamad Zalaf

📞 Contact Information:
📱 Telegram: @MohamadZalaf
📧 Email: 
   • MohamadZalaf@outlook.com
   • Mohamadzalaf2017@gmail.com

━━━━━━━━━━━━━━━
© Mohamad Zalaf 2025""",
        'proxy_quantity': '🔢 Enter the number of proxies needed\n\n📝 Must be a whole number between 1 and 99\n\nExample: 5',
        'invalid_quantity': '❌ Invalid number!\n\n🔢 Please enter a whole number between 1 and 99 only\n❌ Don\'t use decimals or text\n\nCorrect example: 5\nWrong example: 2.5 or five',
        'services_info': 'This is the default services message. Admin can modify it.',
        
        # Balance system messages
        'balance_menu_buttons': ['💳 Recharge Balance', '💰 My Balance', '👥 Referrals', '↩️ Back to Main Menu'],
        'balance_menu_title': '💰 Balance Management\n\nChoose the required operation:',
        'current_balance': '''💰 Your Current Balance:
        
━━━━━━━━━━━━━━━
💳 Charged Balance: {charged_balance:.2f} credits
👥 Referral Balance: {referral_balance:.2f} credits
━━━━━━━━━━━━━━━
🔢 Total Balance: {total_balance:.2f} credits''',
        'recharge_request': '''💳 Balance Recharge Request
        
💎 Credit Price: ${credit_price:.2f} per credit

Choose payment method to continue:''',
        'enter_recharge_amount': '💎 Enter the amount to recharge in USD:\n\nExample: 10',
        'invalid_recharge_amount': '❌ Invalid amount! Please enter a valid number greater than 0',
        'recharge_proof_request': 'Please send payment proof (image only):',
        'recharge_order_created': '✅ Balance recharge request created successfully!\n\n🆔 Order ID: {order_id}\n💰 Amount: ${amount:.2f}\n💎 Expected Credits: {points:.2f} credits\n\n📋 Admin will review the request'
    }
}

# ====== دوال مساعدة عامة ======

def get_syria_time() -> datetime:
    """الحصول على الوقت الحالي بتوقيت سوريا (UTC+3)"""
    syria_tz = pytz.timezone('Asia/Damascus')
    return datetime.now(syria_tz)

def get_syria_time_str(format_str: str = '%Y-%m-%d %H:%M:%S') -> str:
    """الحصول على الوقت الحالي بتوقيت سوريا كنص"""
    return get_syria_time().strftime(format_str)

def escape_markdown_v2(text: str) -> str:
    """
    معالجة النص ليتوافق مع MarkdownV2
    الأحرف الخاصة التي يجب معالجتها: _ * [ ] ( ) ~ ` > # + - = | { } . !
    """
    if not text:
        return ""
    
    # الأحرف الخاصة في MarkdownV2
    special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    
    for char in special_chars:
        text = text.replace(char, f'\\{char}')
    
    return text

def log_with_syria_time(level: str, message: str, user_id: int = None, action: str = None):
    """
    تسجيل رسالة في اللوغز مع الوقت بتوقيت سوريا
    """
    syria_time = get_syria_time_str()
    
    if user_id and action:
        log_message = f"[{syria_time}] [{level}] User {user_id} - {action}: {message}"
    else:
        log_message = f"[{syria_time}] [{level}] {message}"
    
    if level == 'INFO':
        logger.info(log_message)
    elif level == 'ERROR':
        logger.error(log_message)
    elif level == 'WARNING':
        logger.warning(log_message)
    elif level == 'DEBUG':
        logger.debug(log_message)
    else:
        logger.info(log_message)
    
    # تسجيل في قاعدة البيانات إذا كان هناك user_id وaction
    if user_id and action:
        try:
            db.log_action(user_id, action, message)
        except:
            pass

# ====== نهاية دوال المساعدة ======

class DatabaseManager:
    """مدير قاعدة البيانات"""
    
    def __init__(self, db_file: str):
        self.db_file = db_file
        self.init_database()
    
    def init_database(self):
        """إنشاء جداول قاعدة البيانات"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        # جدول المستخدمين
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                language TEXT DEFAULT 'ar',
                referral_balance REAL DEFAULT 0.0,
                credits_balance REAL DEFAULT 0.0,
                referred_by INTEGER,
                join_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_admin BOOLEAN DEFAULT FALSE
            )
        ''')
        
        # جدول الطلبات
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id TEXT PRIMARY KEY,
                user_id INTEGER,
                proxy_type TEXT,
                country TEXT,
                state TEXT,
                payment_method TEXT,
                payment_amount REAL,
                payment_proof TEXT,
                quantity TEXT DEFAULT 'واحد',
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                processed_at TIMESTAMP,
                proxy_details TEXT,
                truly_processed BOOLEAN DEFAULT FALSE,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        # جدول الإحالات
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS referrals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                referrer_id INTEGER,
                referred_id INTEGER,
                amount REAL DEFAULT 0.1,
                activated BOOLEAN DEFAULT FALSE,
                activated_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (referrer_id) REFERENCES users (user_id),
                FOREIGN KEY (referred_id) REFERENCES users (user_id)
            )
        ''')
        
        # جدول الإعدادات
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        ''')
        
        # جدول المعاملات
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id TEXT NOT NULL,
                transaction_number TEXT UNIQUE NOT NULL,
                transaction_type TEXT NOT NULL,  -- 'proxy' or 'withdrawal'
                status TEXT DEFAULT 'completed',  -- 'completed' or 'failed'
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # جدول السجلات
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                action TEXT,
                details TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # إضافة العمود الجديد للطلبات المعالجة فعلياً إذا لم يكن موجوداً
        try:
            cursor.execute("SELECT truly_processed FROM orders LIMIT 1")
        except sqlite3.OperationalError:
            cursor.execute("ALTER TABLE orders ADD COLUMN truly_processed BOOLEAN DEFAULT FALSE")
        
        # إضافة عمود الكمية إذا لم يكن موجوداً
        try:
            cursor.execute("SELECT quantity FROM orders LIMIT 1")
        except sqlite3.OperationalError:
            cursor.execute("ALTER TABLE orders ADD COLUMN quantity TEXT DEFAULT 'واحد'")

        # إضافة أعمدة الإحالة المؤجلة إذا لم تكن موجودة
        try:
            cursor.execute("SELECT activated FROM referrals LIMIT 1")
        except sqlite3.OperationalError:
            cursor.execute("ALTER TABLE referrals ADD COLUMN activated BOOLEAN DEFAULT FALSE")
        
        try:
            cursor.execute("SELECT activated_at FROM referrals LIMIT 1")
        except sqlite3.OperationalError:
            cursor.execute("ALTER TABLE referrals ADD COLUMN activated_at TIMESTAMP")

        # إضافة عمود رصيد الكريديت إذا لم يكن موجوداً
        try:
            cursor.execute("SELECT credits_balance FROM users LIMIT 1")
        except sqlite3.OperationalError:
            cursor.execute("ALTER TABLE users ADD COLUMN credits_balance REAL DEFAULT 0.0")
        
        # إضافة عمود is_banned إذا لم يكن موجوداً
        try:
            cursor.execute("SELECT is_banned FROM users LIMIT 1")
        except sqlite3.OperationalError:
            cursor.execute("ALTER TABLE users ADD COLUMN is_banned BOOLEAN DEFAULT 0")
            print("✅ تم إضافة عمود is_banned")
        
        # إضافة عمود static_type إذا لم يكن موجوداً
        try:
            cursor.execute("SELECT static_type FROM orders LIMIT 1")
        except sqlite3.OperationalError:
            cursor.execute("ALTER TABLE orders ADD COLUMN static_type TEXT DEFAULT ''")
            print("✅ تم إضافة عمود static_type")
        
        # جدول البروكسيات المجانية
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS free_proxies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # جدول نظام الحظر المتدرج
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_bans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                ban_level INTEGER DEFAULT 0,  -- 0: تحذير، 1: 10 دقائق، 2: ساعتين، 3: 24 ساعة
                ban_start_time TIMESTAMP,
                ban_end_time TIMESTAMP,
                is_banned BOOLEAN DEFAULT FALSE,
                warning_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        # جدول تتبع النقرات المتكررة
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS click_tracking (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                last_click_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                click_count INTEGER DEFAULT 1,
                reset_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')

        # جدول معاملات النقاط
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS credits_transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                transaction_type TEXT NOT NULL,  -- 'charge', 'spend', 'refund'
                amount REAL NOT NULL,
                order_id TEXT,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id),
                FOREIGN KEY (order_id) REFERENCES orders (id)
            )
        ''')

        # جدول إدارة حالة الخدمات (تشغيل/إيقاف)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS service_status (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                service_type TEXT NOT NULL,  -- 'static' or 'socks'
                service_subtype TEXT,  -- 'monthly_residential', 'weekly_static', etc.
                country_code TEXT,  -- 'US', 'UK', 'FR', etc.
                state_code TEXT,  -- 'CA', 'NY', 'TX', etc. (NULL for countries without states)
                is_enabled BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(service_type, service_subtype, country_code, state_code)
            )
        ''')

        # إضافة الإعدادات الافتراضية
        cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('credit_price', '1.0')")  # سعر الكريديت الواحد بالدولار
        
        # إدراج البيانات الافتراضية لحالة الخدمات (جميع الخدمات مفعلة بشكل افتراضي)
        self._insert_default_service_status(cursor)
        
        conn.commit()
        conn.close()
    
    def _insert_default_service_status(self, cursor):
        """إدراج حالة الخدمات الافتراضية (جميعها مفعلة)"""
        # خدمات ستاتيك
        static_services = [
            ('static', 'monthly_residential', None, None),
            ('static', 'monthly_verizon', None, None), 
            ('static', 'weekly_crocker', None, None),
            ('static', 'daily_static', None, None),
            ('static', 'isp_att', None, None),
            ('static', 'datacenter', None, None)
        ]
        
        # إضافة دول ستاتيك
        for country in ['US', 'UK', 'FR', 'DE', 'AT']:
            static_services.append(('static', 'basic', country, None))
        
        # إضافة ولايات أمريكا للخدمات المختلفة
        us_states = ['NY', 'CA', 'TX', 'FL', 'AZ', 'DE', 'VA', 'WA', 'MA']
        for state in us_states:
            static_services.extend([
                ('static', 'monthly_residential', 'US', state),
                ('static', 'monthly_verizon', 'US', state),
                ('static', 'weekly_crocker', 'US', state),
                ('static', 'datacenter', 'US', state),
                ('static', 'isp_att', 'US', state)
            ])
        
        # خدمات سوكس
        socks_services = [
            ('socks', 'basic', None, None),
            ('socks', 'single', None, None),
            ('socks', 'package_2', None, None),
            ('socks', 'package_5', None, None),
            ('socks', 'package_10', None, None)
        ]
        
        # إضافة دول سوكس لجميع الأنواع الفرعية
        for country in ['US', 'FR', 'ES', 'UK', 'CA', 'DE', 'IT', 'SE']:
            for socks_type in ['basic', 'single', 'package_2', 'package_5', 'package_10']:
                socks_services.append(('socks', socks_type, country, None))
        
        # إضافة ولايات أمريكا للسوكس لجميع الأنواع الفرعية
        for state in us_states:
            for socks_type in ['basic', 'single', 'package_2', 'package_5', 'package_10']:
                socks_services.append(('socks', socks_type, 'US', state))
        
        # إدراج جميع الخدمات
        all_services = static_services + socks_services
        for service in all_services:
            cursor.execute("""
                INSERT OR IGNORE INTO service_status 
                (service_type, service_subtype, country_code, state_code, is_enabled) 
                VALUES (?, ?, ?, ?, TRUE)
            """, service)
    
    def execute_query(self, query: str, params: tuple = ()) -> List[tuple]:
        """تنفيذ استعلام قاعدة البيانات"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_file, timeout=30.0)
            cursor = conn.cursor()
            cursor.execute(query, params)
            result = cursor.fetchall()
            conn.commit()
            return result
        except sqlite3.Error as e:
            logger.error(f"Database error in execute_query: {e}")
            logger.error(f"Query: {query}")
            logger.error(f"Params: {params}")
            if conn:
                conn.rollback()
            return []
        except Exception as e:
            logger.error(f"Unexpected error in execute_query: {e}")
            if conn:
                conn.rollback()
            return []
        finally:
            if conn:
                conn.close()
    
    def add_user(self, user_id: int, username: str, first_name: str, last_name: str, referred_by: int = None, language: str = None):
        """إضافة مستخدم جديد"""
        if language:
            query = '''
                INSERT OR IGNORE INTO users (user_id, username, first_name, last_name, referred_by, language)
                VALUES (?, ?, ?, ?, ?, ?)
            '''
            self.execute_query(query, (user_id, username, first_name, last_name, referred_by, language))
        else:
            query = '''
                INSERT OR IGNORE INTO users (user_id, username, first_name, last_name, referred_by)
                VALUES (?, ?, ?, ?, ?)
            '''
            self.execute_query(query, (user_id, username, first_name, last_name, referred_by))
    
    def get_user(self, user_id: int) -> Optional[tuple]:
        """الحصول على بيانات المستخدم"""
        query = "SELECT * FROM users WHERE user_id = ?"
        result = self.execute_query(query, (user_id,))
        return result[0] if result else None
    
    def update_user_language(self, user_id: int, language: str):
        """تحديث لغة المستخدم"""
        query = "UPDATE users SET language = ? WHERE user_id = ?"
        self.execute_query(query, (language, user_id))
    
    # دوال إدارة الرصيد والكريديت
    def get_user_balance(self, user_id: int) -> Dict[str, float]:
        """الحصول على رصيد المستخدم (رصيد الإحالات + رصيد الكريديت)"""
        user_data = self.get_user(user_id)
        if user_data:
            # user_data structure: (user_id, username, first_name, last_name, language, referral_balance, credits_balance, referred_by, join_date, is_admin)
            referral_balance = float(user_data[5] or 0.0)
            credits_balance = float(user_data[6] or 0.0)
            total_balance = referral_balance + credits_balance
            
            return {
                'referral_balance': referral_balance,
                'charged_balance': credits_balance,
                'total_balance': total_balance
            }
        return {'referral_balance': 0.0, 'charged_balance': 0.0, 'total_balance': 0.0}
    
    def add_credits(self, user_id: int, amount: float, transaction_type: str, order_id: str = None, description: str = ""):
        """إضافة كريديت إلى رصيد المستخدم"""
        # تحديث رصيد الكريديت
        query = "UPDATE users SET credits_balance = credits_balance + ? WHERE user_id = ?"
        self.execute_query(query, (amount, user_id))
        
        # إضافة معاملة الكريديت
        self.add_credits_transaction(user_id, transaction_type, amount, order_id, description)
    
    def deduct_credits(self, user_id: int, amount: float, transaction_type: str, order_id: str = None, description: str = "", allow_negative: bool = True):
        """خصم كريديت من رصيد المستخدم (من الرصيد المشحون أولاً ثم الإحالات)"""
        balance = self.get_user_balance(user_id)
        total_balance = balance['total_balance']
        charged_balance = balance['charged_balance']
        referral_balance = balance['referral_balance']
        
        # فحص كفاية الرصيد فقط إذا لم يكن مسموح بالقيم السالبة
        if not allow_negative and total_balance < amount:
            raise ValueError(f"Insufficient total balance. Required: {amount}, Available: {total_balance}")
        
        # حساب المبالغ المطلوبة للخصم
        if charged_balance >= amount:
            # الرصيد المشحون يكفي لوحده
            charged_deduction = amount
            referral_deduction = 0.0
        else:
            # نحتاج للخصم من كلا الرصيدين (حتى لو أصبح سالباً)
            charged_deduction = charged_balance  # خصم كامل الرصيد المشحون
            referral_deduction = amount - charged_balance  # خصم الباقي من الإحالات (قد يصبح سالباً)
        
        # تنفيذ عمليات الخصم (يقبل القيم السالبة)
        if charged_deduction > 0:
            query = "UPDATE users SET credits_balance = credits_balance - ? WHERE user_id = ?"
            self.execute_query(query, (charged_deduction, user_id))
            
        if referral_deduction > 0:
            query = "UPDATE users SET referral_balance = referral_balance - ? WHERE user_id = ?"
            self.execute_query(query, (referral_deduction, user_id))
        
        # إضافة معاملة النقاط (بقيمة سالبة للدلالة على الخصم)
        deduction_description = f"خصم: {charged_deduction:.2f} من الرصيد المشحون"
        if referral_deduction > 0:
            deduction_description += f" + {referral_deduction:.2f} من رصيد الإحالات"
        if description:
            deduction_description += f" - {description}"
            
        self.add_credits_transaction(user_id, transaction_type, -amount, order_id, deduction_description)
    
    def add_credits_transaction(self, user_id: int, transaction_type: str, amount: float, order_id: str = None, description: str = ""):
        """إضافة معاملة كريديت جديدة"""
        query = '''
            INSERT INTO credits_transactions (user_id, transaction_type, amount, order_id, description)
            VALUES (?, ?, ?, ?, ?)
        '''
        self.execute_query(query, (user_id, transaction_type, amount, order_id, description))
    
    def get_credit_price(self) -> float:
        """الحصول على سعر الكريديت الواحد"""
        query = "SELECT value FROM settings WHERE key = 'credit_price'"
        result = self.execute_query(query)
        if result:
            return float(result[0][0])
        return 1.0  # القيمة الافتراضية
    
    def set_credit_price(self, price: float):
        """تعديل سعر الكريديت الواحد"""
        query = "INSERT OR REPLACE INTO settings (key, value) VALUES ('credit_price', ?)"
        self.execute_query(query, (str(price),))
    
    # دوال إدارة حالة الخدمات (تشغيل/إيقاف)
    def get_service_status(self, service_type: str, service_subtype: str = None, 
                          country_code: str = None, state_code: str = None) -> bool:
        """الحصول على حالة خدمة معينة"""
        query = """
            SELECT is_enabled FROM service_status 
            WHERE service_type = ? AND 
                  (service_subtype = ? OR (service_subtype IS NULL AND ? IS NULL)) AND
                  (country_code = ? OR (country_code IS NULL AND ? IS NULL)) AND
                  (state_code = ? OR (state_code IS NULL AND ? IS NULL))
        """
        result = self.execute_query(query, (service_type, service_subtype, service_subtype, 
                                           country_code, country_code, state_code, state_code))
        return bool(result[0][0]) if result else True  # افتراضياً مفعل
    
    def set_service_status(self, service_type: str, is_enabled: bool, 
                          service_subtype: str = None, country_code: str = None, 
                          state_code: str = None):
        """تحديد حالة خدمة معينة"""
        query = """
            INSERT OR REPLACE INTO service_status 
            (service_type, service_subtype, country_code, state_code, is_enabled, updated_at) 
            VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """
        self.execute_query(query, (service_type, service_subtype, country_code, state_code, is_enabled))
    
    def get_service_subtypes_status(self, service_type: str) -> Dict[str, bool]:
        """الحصول على حالة جميع الأنواع الفرعية لخدمة معينة"""
        query = """
            SELECT service_subtype, is_enabled FROM service_status 
            WHERE service_type = ? AND country_code IS NULL AND state_code IS NULL
        """
        result = self.execute_query(query, (service_type,))
        return {subtype: bool(enabled) for subtype, enabled in result if subtype}
    
    def get_countries_status(self, service_type: str, service_subtype: str = None) -> Dict[str, bool]:
        """الحصول على حالة جميع الدول لخدمة معينة"""
        if service_subtype:
            query = """
                SELECT country_code, is_enabled FROM service_status 
                WHERE service_type = ? AND service_subtype = ? AND country_code IS NOT NULL AND state_code IS NULL
            """
            result = self.execute_query(query, (service_type, service_subtype))
        else:
            query = """
                SELECT country_code, is_enabled FROM service_status 
                WHERE service_type = ? AND country_code IS NOT NULL AND state_code IS NULL
            """
            result = self.execute_query(query, (service_type,))
        return {country: bool(enabled) for country, enabled in result if country}
    
    def get_states_status(self, service_type: str, country_code: str, 
                         service_subtype: str = None) -> Dict[str, bool]:
        """الحصول على حالة جميع الولايات لدولة معينة"""
        if service_subtype:
            query = """
                SELECT state_code, is_enabled FROM service_status 
                WHERE service_type = ? AND service_subtype = ? AND country_code = ? AND state_code IS NOT NULL
            """
            result = self.execute_query(query, (service_type, service_subtype, country_code))
        else:
            query = """
                SELECT state_code, is_enabled FROM service_status 
                WHERE service_type = ? AND country_code = ? AND state_code IS NOT NULL
            """
            result = self.execute_query(query, (service_type, country_code))
        return {state: bool(enabled) for state, enabled in result if state}
    
    def toggle_all_service_subtypes(self, service_type: str, is_enabled: bool):
        """تشغيل/إيقاف جميع الأنواع الفرعية لخدمة معينة"""
        query = """
            UPDATE service_status SET is_enabled = ?, updated_at = CURRENT_TIMESTAMP
            WHERE service_type = ?
        """
        self.execute_query(query, (is_enabled, service_type))
    
    def toggle_all_countries(self, service_type: str, service_subtype: str, is_enabled: bool):
        """تشغيل/إيقاف جميع دول نوع خدمة معين"""
        if service_subtype:
            query = """
                UPDATE service_status SET is_enabled = ?, updated_at = CURRENT_TIMESTAMP
                WHERE service_type = ? AND service_subtype = ?
            """
            self.execute_query(query, (is_enabled, service_type, service_subtype))
        else:
            query = """
                UPDATE service_status SET is_enabled = ?, updated_at = CURRENT_TIMESTAMP
                WHERE service_type = ?
            """
            self.execute_query(query, (is_enabled, service_type))
    
    def toggle_all_states(self, service_type: str, country_code: str, 
                         service_subtype: str, is_enabled: bool):
        """تشغيل/إيقاف جميع ولايات دولة معينة"""
        query = """
            UPDATE service_status SET is_enabled = ?, updated_at = CURRENT_TIMESTAMP
            WHERE service_type = ? AND service_subtype = ? AND country_code = ? AND state_code IS NOT NULL
        """
        self.execute_query(query, (is_enabled, service_type, service_subtype, country_code))
    
    def get_service_statistics(self, service_type: str) -> dict:
        """إحصائيات الخدمة لنوع خدمة معين"""
        try:
            # عدد الطلبات المعالجة لهذا النوع
            query_orders = """
                SELECT COUNT(*) FROM orders 
                WHERE proxy_type = ? AND status = 'processed'
            """
            processed_orders = self.execute_query(query_orders, (service_type,))
            processed_count = processed_orders[0][0] if processed_orders else 0
            
            # عدد الطلبات المعلقة لهذا النوع
            query_pending = """
                SELECT COUNT(*) FROM orders 
                WHERE proxy_type = ? AND status = 'pending'
            """
            pending_orders = self.execute_query(query_pending, (service_type,))
            pending_count = pending_orders[0][0] if pending_orders else 0
            
            # عدد الخدمات المفعلة لهذا النوع
            query_enabled = """
                SELECT COUNT(*) FROM service_status 
                WHERE service_type = 'static' AND service_subtype = ? AND is_enabled = 1
            """
            enabled_services = self.execute_query(query_enabled, (service_type,))
            enabled_count = enabled_services[0][0] if enabled_services else 0
            
            # عدد الخدمات المعطلة لهذا النوع
            query_disabled = """
                SELECT COUNT(*) FROM service_status 
                WHERE service_type = 'static' AND service_subtype = ? AND is_enabled = 0
            """
            disabled_services = self.execute_query(query_disabled, (service_type,))
            disabled_count = disabled_services[0][0] if disabled_services else 0
            
            return {
                'processed_orders': processed_count,
                'pending_orders': pending_count,
                'enabled_services': enabled_count,
                'disabled_services': disabled_count,
                'total_services': enabled_count + disabled_count
            }
        except Exception as e:
            logger.error(f"Error getting service statistics for {service_type}: {e}")
            return {
                'processed_orders': 0,
                'pending_orders': 0,
                'enabled_services': 0,
                'disabled_services': 0,
                'total_services': 0
            }
    
    def create_recharge_order(self, order_id: str, user_id: int, amount: float, expected_credits: float):
        """إنشاء طلب شحن رصيد"""
        query = '''
            INSERT INTO orders (id, user_id, proxy_type, country, state, payment_method, payment_amount, quantity)
            VALUES (?, ?, 'balance_recharge', '', '', '', ?, ?)
        '''
        self.execute_query(query, (order_id, user_id, amount, f'{expected_credits:.2f} points'))
    
    def create_order(self, order_id: str, user_id: int, proxy_type: str, country: str, state: str, payment_method: str, payment_amount: float = 0.0, quantity: str = "5"):
        """إنشاء طلب جديد"""
        # التحقق من وجود عمود static_type وإضافته إذا لزم الأمر (بطريقة آمنة)
        conn = None
        try:
            conn = sqlite3.connect(self.db_file, timeout=30.0)
            cursor = conn.cursor()
            
            # فحص وجود العمود باستخدام PRAGMA
            cursor.execute("PRAGMA table_info(orders)")
            columns = [column[1] for column in cursor.fetchall()]
            
            # إضافة العمود فقط إذا لم يكن موجوداً
            if 'static_type' not in columns:
                try:
                    cursor.execute("ALTER TABLE orders ADD COLUMN static_type TEXT DEFAULT ''")
                    conn.commit()
                    logger.info("✅ Column 'static_type' added to orders table successfully")
                except sqlite3.OperationalError as e:
                    # تجاهل الخطأ إذا كان العمود موجوداً بالفعل
                    if "duplicate column" not in str(e).lower():
                        raise
                    logger.info("ℹ️ Column 'static_type' already exists")
        except sqlite3.Error as e:
            logger.error(f"⚠️ Database error in create_order: {e}")
        finally:
            if conn:
                conn.close()
            
        # إنشاء الطلب
        query = '''
            INSERT INTO orders (id, user_id, proxy_type, country, state, payment_method, payment_amount, quantity, static_type)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        self.execute_query(query, (order_id, user_id, proxy_type, country, state, payment_method, payment_amount, quantity, ''))
    
    def update_order_payment_proof(self, order_id: str, payment_proof: str):
        """تحديث إثبات الدفع للطلب"""
        query = "UPDATE orders SET payment_proof = ? WHERE id = ?"
        self.execute_query(query, (payment_proof, order_id))
    
    def get_pending_orders(self) -> List[tuple]:
        """الحصول على الطلبات المعلقة"""
        try:
            query = "SELECT * FROM orders WHERE status = 'pending' ORDER BY created_at DESC"
            result = self.execute_query(query)
            return result if result else []
        except Exception as e:
            logger.error(f"Error in get_pending_orders: {e}")
            print(f"❌ خطأ في استعلام الطلبات المعلقة: {e}")
            return []
    
    def log_action(self, user_id: int, action: str, details: str = ""):
        """تسجيل إجراء في السجل"""
        syria_time = get_syria_time_str()
        query = "INSERT INTO logs (user_id, action, details, timestamp) VALUES (?, ?, ?, ?)"
        self.execute_query(query, (user_id, action, f"[{syria_time}] {details}", syria_time))
    
    def get_old_payment_proofs(self, days_old: int = 30) -> List[tuple]:
        """
        الحصول على صور التأكيد القديمة (أقدم من X يوم)
        لحذفها وتحرير المساحة
        """
        query = """
            SELECT id, payment_proof, created_at, status 
            FROM orders 
            WHERE payment_proof LIKE 'photo:%' 
            AND created_at < datetime('now', '-' || ? || ' days')
            AND status IN ('completed', 'rejected')
        """
        return self.execute_query(query, (days_old,))
    
    def clear_old_payment_proofs(self, days_old: int = 30) -> int:
        """
        حذف صور التأكيد القديمة من الطلبات المكتملة/المرفوضة
        إرجاع: عدد السجلات المحدثة
        """
        # الحصول على الصور القديمة أولاً
        old_proofs = self.get_old_payment_proofs(days_old)
        
        if not old_proofs:
            return 0
        
        # حذف المرجع للصورة من قاعدة البيانات
        query = """
            UPDATE orders 
            SET payment_proof = NULL 
            WHERE payment_proof LIKE 'photo:%' 
            AND created_at < datetime('now', '-' || ? || ' days')
            AND status IN ('completed', 'rejected')
        """
        self.execute_query(query, (days_old,))
        
        logger.info(f"Cleared {len(old_proofs)} old payment proofs (older than {days_old} days)")
        return len(old_proofs)
    
    def get_payment_proofs_stats(self) -> dict:
        """
        إحصائيات صور التأكيد في قاعدة البيانات
        """
        stats = {
            'total_with_photos': 0,
            'pending_with_photos': 0,
            'completed_with_photos': 0,
            'rejected_with_photos': 0,
            'old_photos_30days': 0,
            'old_photos_60days': 0,
            'old_photos_90days': 0
        }
        
        # إجمالي الطلبات مع صور
        result = self.execute_query("SELECT COUNT(*) FROM orders WHERE payment_proof LIKE 'photo:%'")
        stats['total_with_photos'] = result[0][0] if result else 0
        
        # حسب الحالة
        for status in ['pending', 'completed', 'rejected']:
            result = self.execute_query(
                "SELECT COUNT(*) FROM orders WHERE payment_proof LIKE 'photo:%' AND status = ?",
                (status,)
            )
            stats[f'{status}_with_photos'] = result[0][0] if result else 0
        
        # الصور القديمة
        for days in [30, 60, 90]:
            result = self.execute_query(
                """SELECT COUNT(*) FROM orders 
                   WHERE payment_proof LIKE 'photo:%' 
                   AND created_at < datetime('now', '-' || ? || ' days')
                   AND status IN ('completed', 'rejected')""",
                (days,)
            )
            stats[f'old_photos_{days}days'] = result[0][0] if result else 0
        
        return stats
    
    def get_truly_processed_orders(self) -> List[tuple]:
        """الحصول على الطلبات المعالجة فعلياً فقط (وفقاً للشرطين المحددين)"""
        return self.execute_query("SELECT * FROM orders WHERE truly_processed = TRUE")
    
    def get_unprocessed_orders(self) -> List[tuple]:
        """الحصول على الطلبات غير المعالجة فعلياً (بغض النظر عن الحالة)"""
        return self.execute_query("SELECT * FROM orders WHERE truly_processed = FALSE OR truly_processed IS NULL")
    
    def validate_database_integrity(self) -> dict:
        """فحص سلامة قاعدة البيانات"""
        try:
            validation_results = {
                'database_accessible': True,
                'tables_exist': True,
                'data_integrity': True,
                'errors': []
            }
            
            # فحص إمكانية الوصول لقاعدة البيانات
            try:
                conn = sqlite3.connect(self.db_file, timeout=10.0)
                conn.close()
            except Exception as e:
                validation_results['database_accessible'] = False
                validation_results['errors'].append(f"Database access error: {e}")
                return validation_results
            
            # فحص وجود الجداول المطلوبة
            required_tables = ['users', 'orders', 'referrals', 'settings', 'transactions', 'logs']
            existing_tables = self.execute_query("SELECT name FROM sqlite_master WHERE type='table'")
            existing_table_names = [table[0] for table in existing_tables]
            
            for table in required_tables:
                if table not in existing_table_names:
                    validation_results['tables_exist'] = False
                    validation_results['errors'].append(f"Missing table: {table}")
            
            # فحص سلامة البيانات
            try:
                # فحص الطلبات بدون مستخدمين
                orphaned_orders = self.execute_query("""
                    SELECT COUNT(*) FROM orders 
                    WHERE user_id NOT IN (SELECT user_id FROM users)
                """)
                if orphaned_orders and orphaned_orders[0][0] > 0:
                    validation_results['data_integrity'] = False
                    validation_results['errors'].append(f"Orphaned orders: {orphaned_orders[0][0]}")
                
                # فحص الطلبات التالفة
                corrupt_orders = self.execute_query("""
                    SELECT COUNT(*) FROM orders 
                    WHERE id IS NULL OR user_id IS NULL OR proxy_type IS NULL
                """)
                if corrupt_orders and corrupt_orders[0][0] > 0:
                    validation_results['data_integrity'] = False
                    validation_results['errors'].append(f"Corrupt orders: {corrupt_orders[0][0]}")
                    
            except Exception as e:
                validation_results['data_integrity'] = False
                validation_results['errors'].append(f"Data integrity check failed: {e}")
            
            return validation_results
            
        except Exception as e:
            return {
                'database_accessible': False,
                'tables_exist': False,
                'data_integrity': False,
                'errors': [f"Validation failed: {e}"]
            }

# ===== نظام الحظر المتدرج =====

def track_user_click(user_id: int) -> tuple:
    """تتبع النقرات المتكررة للمستخدم وإرجاع (عدد النقرات, الوقت منذ آخر نقرة)"""
    from datetime import datetime, timedelta
    
    current_time = datetime.now()
    
    # فحص النقرات الموجودة للمستخدم
    query = "SELECT click_count, last_click_time, reset_time FROM click_tracking WHERE user_id = ?"
    result = db.execute_query(query, (user_id,))
    
    if result:
        click_count, last_click_str, reset_time_str = result[0]
        last_click_time = datetime.fromisoformat(last_click_str)
        reset_time = datetime.fromisoformat(reset_time_str)
        
        # إعادة تعيين العداد إذا مر أكثر من 5 ثانية على آخر نقرة
        if (current_time - last_click_time).seconds > 5:
            click_count = 1
            reset_time = current_time
        else:
            click_count += 1
        
        # تحديث السجل
        update_query = "UPDATE click_tracking SET click_count = ?, last_click_time = ?, reset_time = ? WHERE user_id = ?"
        db.execute_query(update_query, (click_count, current_time.isoformat(), reset_time.isoformat(), user_id))
        
    else:
        # إنشاء سجل جديد للمستخدم
        click_count = 1
        reset_time = current_time
        insert_query = "INSERT INTO click_tracking (user_id, click_count, last_click_time, reset_time) VALUES (?, ?, ?, ?)"
        db.execute_query(insert_query, (user_id, click_count, current_time.isoformat(), reset_time.isoformat()))
    
    return click_count, (current_time - reset_time).seconds

def is_user_banned(user_id: int) -> tuple:
    """فحص ما إذا كان المستخدم محظوراً - إرجاع (محظور؟, مستوى الحظر, وقت انتهاء الحظر)"""
    from datetime import datetime
    
    query = "SELECT is_banned, ban_level, ban_end_time FROM user_bans WHERE user_id = ? ORDER BY created_at DESC LIMIT 1"
    result = db.execute_query(query, (user_id,))
    
    if result:
        is_banned, ban_level, ban_end_time_str = result[0]
        if is_banned and ban_end_time_str:
            ban_end_time = datetime.fromisoformat(ban_end_time_str)
            # فحص ما إذا كان الحظر انتهى
            if datetime.now() >= ban_end_time:
                # رفع الحظر تلقائياً مع الإشعارات
                was_lifted = lift_user_ban(user_id)
                if was_lifted:
                    # إضافة مهمة الإشعار إلى قائمة الانتظار
                    global pending_unban_notifications
                    if 'pending_unban_notifications' not in globals():
                        pending_unban_notifications = []
                    pending_unban_notifications.append(user_id)
                return False, 0, None
            else:
                return True, ban_level, ban_end_time
        else:
            return False, 0, None
    else:
        return False, 0, None

def apply_progressive_ban(user_id: int, click_count: int) -> str:
    """تطبيق نظام الحظر المتدرج بناءً على عدد النقرات"""
    from datetime import datetime, timedelta
    
    current_time = datetime.now()
    
    # فحص مستوى الحظر الحالي
    query = "SELECT ban_level, warning_count FROM user_bans WHERE user_id = ? ORDER BY created_at DESC LIMIT 1"
    result = db.execute_query(query, (user_id,))
    
    if result:
        current_ban_level, warning_count = result[0]
    else:
        current_ban_level = 0
        warning_count = 0
    
    # تحديد المرحلة بناءً على عدد النقرات (15-17 مرة)
    if 15 <= click_count <= 17:
        if current_ban_level == 0:  # تحذير
            warning_count += 1
            if warning_count >= 2:  # بعد تحذيرين، ننتقل للحظر الأول
                # حظر 10 دقائق
                ban_end_time = current_time + timedelta(minutes=10)
                insert_or_update_ban(user_id, 1, current_time, ban_end_time, True, warning_count)
                return "ban_10_min"
            else:
                # تحذير
                insert_or_update_ban(user_id, 0, current_time, None, False, warning_count)
                return "warning"
                
        elif current_ban_level == 1:  # من 10 دقائق إلى ساعتين
            ban_end_time = current_time + timedelta(hours=2)
            insert_or_update_ban(user_id, 2, current_time, ban_end_time, True, warning_count)
            return "ban_2_hours"
            
        elif current_ban_level == 2:  # من ساعتين إلى 24 ساعة
            ban_end_time = current_time + timedelta(hours=24)
            insert_or_update_ban(user_id, 3, current_time, ban_end_time, True, warning_count)
            return "ban_24_hours"
    
    return "no_action"

def insert_or_update_ban(user_id: int, ban_level: int, start_time: datetime, end_time: datetime = None, is_banned: bool = False, warning_count: int = 0):
    """إدراج أو تحديث سجل الحظر"""
    # فحص ما إذا كان هناك سجل موجود
    existing_query = "SELECT id FROM user_bans WHERE user_id = ?"
    result = db.execute_query(existing_query, (user_id,))
    
    if result:
        # تحديث السجل الموجود
        update_query = """
            UPDATE user_bans 
            SET ban_level = ?, ban_start_time = ?, ban_end_time = ?, is_banned = ?, warning_count = ?, updated_at = ?
            WHERE user_id = ?
        """
        end_time_str = end_time.isoformat() if end_time else None
        db.execute_query(update_query, (ban_level, start_time.isoformat(), end_time_str, is_banned, warning_count, start_time.isoformat(), user_id))
    else:
        # إنشاء سجل جديد
        insert_query = """
            INSERT INTO user_bans (user_id, ban_level, ban_start_time, ban_end_time, is_banned, warning_count)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        end_time_str = end_time.isoformat() if end_time else None
        db.execute_query(insert_query, (user_id, ban_level, start_time.isoformat(), end_time_str, is_banned, warning_count))

def lift_user_ban(user_id: int) -> bool:
    """رفع الحظر عن المستخدم - إرجاع True إذا تم رفع الحظر فعلاً"""
    from datetime import datetime
    
    # فحص ما إذا كان المستخدم محظوراً حالياً
    check_query = "SELECT is_banned FROM user_bans WHERE user_id = ? AND is_banned = TRUE"
    result = db.execute_query(check_query, (user_id,))
    
    if result:
        # رفع الحظر
        update_query = "UPDATE user_bans SET is_banned = FALSE, updated_at = ? WHERE user_id = ?"
        db.execute_query(update_query, (datetime.now().isoformat(), user_id))
        return True  # تم رفع الحظر
    
    return False  # لم يكن محظوراً أساساً

def reset_user_clicks(user_id: int):
    """إعادة تعيين عداد النقرات للمستخدم"""
    from datetime import datetime
    
    query = "UPDATE click_tracking SET click_count = 0, reset_time = ? WHERE user_id = ?"
    db.execute_query(query, (datetime.now().isoformat(), user_id))

async def send_warning_message(context, chat_id: int):
    """إرسال رسالة التحذير للمستخدم مع إيقاف مؤقت"""
    import asyncio
    
    try:
        # إرسال الرسالة الأولى
        await context.bot.send_message(chat_id=chat_id, text="⚠️")
        
        # انتظار قصير
        await asyncio.sleep(1)
        
        # إرسال الرسالة الثانية
        await context.bot.send_message(
            chat_id=chat_id, 
            text="⚠️ لقد تم الاشتباه بنشاط تخريبي، الرجاء الحذر قد يؤدي الاستمرار في هذا النهج إلى حظرك"
        )
        
        # إيقاف الاستجابة 10 ثواني
        await asyncio.sleep(10)
        
    except Exception as e:
        logger.error(f"Error sending warning message to {chat_id}: {e}")

async def send_ban_message(context, chat_id: int, ban_type: str):
    """إرسال رسالة الحظر حسب النوع"""
    import asyncio
    
    try:
        if ban_type == "ban_10_min":
            await context.bot.send_message(
                chat_id=chat_id,
                text="⚠️ عذراً تم حظرك 10 دقائق، نعتذر في حال وجود خطأ ما، الرجاء مراجعة الدعم @Static_support"
            )
            
        elif ban_type == "ban_2_hours":
            # إرسال الرسالة الأولى
            await context.bot.send_message(chat_id=chat_id, text="🤨")
            
            # انتظار قصير
            await asyncio.sleep(1)
            
            # إرسال الرسالة الثانية
            await context.bot.send_message(
                chat_id=chat_id,
                text="ما بك ؟ 🤨\nهل تتقصد الإزعاج و التخريب؟...حسناً...إليك ساعتي حظر 😊"
            )
            
        elif ban_type == "ban_24_hours":
            await context.bot.send_message(
                chat_id=chat_id,
                text="عذرا عزيزي المستخدم تم تحديد نشاطك على إنه إزعاج مقصود، سنضطر لحظرك 24 ساعة...نهاراً سعيداً 👍"
            )
            
    except Exception as e:
        logger.error(f"Error sending ban message ({ban_type}) to {chat_id}: {e}")

async def notify_admin_ban(context, user_id: int, ban_type: str, username: str = ""):
    """إخبار الآدمن النشطين عن حظر مستخدم"""
    try:
        global ACTIVE_ADMINS
        
        # إذا لم يكن هناك آدمن نشطين، لا ترسل إشعارات
        if not ACTIVE_ADMINS:
            return
            
        ban_messages = {
            "warning": "تحذير مستخدم",
            "ban_10_min": "حظر 10 دقائق", 
            "ban_2_hours": "حظر ساعتين",
            "ban_24_hours": "حظر 24 ساعة"
        }
        
        ban_text = ban_messages.get(ban_type, ban_type)
        user_text = f"@{username}" if username else f"ID: {user_id}"
        message = f"🚨 تم {ban_text} للمستخدم {user_text}\n⚠️ السبب: نشاط تخريبي (نقرات متكررة)"
        
        # إرسال الإشعار لجميع الآدمن النشطين
        for admin_id in ACTIVE_ADMINS:
            try:
                await context.bot.send_message(
                    chat_id=admin_id,
                    text=message
                )
            except Exception as e:
                logger.error(f"Error sending ban notification to admin {admin_id}: {e}")
                
    except Exception as e:
        logger.error(f"Error notifying admins about ban: {e}")

async def notify_admin_unban(context_or_app, user_id: int, username: str = ""):
    """إخبار الآدمن النشطين عن رفع حظر مستخدم"""
    try:
        global ACTIVE_ADMINS
        
        # إذا لم يكن هناك آدمن نشطين، لا ترسل إشعارات
        if not ACTIVE_ADMINS:
            return
            
        user_text = f"@{username}" if username else f"ID: {user_id}"
        message = f"✅ تم رفع الحظر عن المستخدم {user_text}"
        
        # إرسال الإشعار لجميع الآدمن النشطين
        for admin_id in ACTIVE_ADMINS:
            try:
                if hasattr(context_or_app, 'bot'):
                    # إذا كان context
                    await context_or_app.bot.send_message(
                        chat_id=admin_id,
                        text=message
                    )
                else:
                    # إذا كان application
                    await context_or_app.bot.send_message(
                        chat_id=admin_id,
                        text=message
                    )
            except Exception as e:
                logger.error(f"Error sending unban notification to admin {admin_id}: {e}")
                
    except Exception as e:
        logger.error(f"Error notifying admins about unban: {e}")

async def notify_user_unban(context_or_app, chat_id: int):
    """إخبار المستخدم عن رفع الحظر"""
    try:
        if hasattr(context_or_app, 'bot'):
            # إذا كان context
            await context_or_app.bot.send_message(
                chat_id=chat_id,
                text="✅ تم رفع الحظر عنك، يمكنك الآن استخدام البوت بشكل طبيعي"
            )
        else:
            # إذا كان application
            await context_or_app.bot.send_message(
                chat_id=chat_id,
                text="✅ تم رفع الحظر عنك، يمكنك الآن استخدام البوت بشكل طبيعي"
            )
    except Exception as e:
        logger.error(f"Error notifying user about unban: {e}")

async def check_user_ban_and_track_clicks(update, context) -> bool:
    """
    فحص حظر المستخدم وتتبع النقرات المتكررة
    إرجاع True إذا كان المستخدم محظوراً أو تم تطبيق إجراء (يجب إيقاف المعالجة)
    إرجاع False إذا كان بإمكان المتابعة بشكل طبيعي
    """
    try:
        user = update.effective_user
        if not user:
            return False
            
        user_id = user.id
        username = user.username or ""
        
        # فحص ما إذا كان المستخدم محظوراً حالياً
        is_banned_status, ban_level, ban_end_time = is_user_banned(user_id)
        
        if is_banned_status:
            # المستخدم محظور، لا نرد عليه
            logger.info(f"User {user_id} is banned until {ban_end_time}")
            return True
        
        # تتبع النقرات المتكررة
        click_count, elapsed_time = track_user_click(user_id)
        
        # فحص النقرات المتكررة (15-17 نقرة متتالية)
        if 15 <= click_count <= 17:
            ban_action = apply_progressive_ban(user_id, click_count)
            
            if ban_action == "warning":
                # إرسال تحذير
                await send_warning_message(context, user_id)
                await notify_admin_ban(context, user_id, "warning", username)
                return True  # إيقاف المعالجة
                
            elif ban_action == "ban_10_min":
                # حظر 10 دقائق
                await send_ban_message(context, user_id, "ban_10_min")
                await notify_admin_ban(context, user_id, "ban_10_min", username)
                return True  # إيقاف المعالجة
                
            elif ban_action == "ban_2_hours":
                # حظر ساعتين
                await send_ban_message(context, user_id, "ban_2_hours")
                await notify_admin_ban(context, user_id, "ban_2_hours", username)
                return True  # إيقاف المعالجة
                
            elif ban_action == "ban_24_hours":
                # حظر 24 ساعة
                await send_ban_message(context, user_id, "ban_24_hours")
                await notify_admin_ban(context, user_id, "ban_24_hours", username)
                return True  # إيقاف المعالجة
        
        # إعادة تعيين النقرات إذا مر وقت كافي (أكثر من 5 ثوان)
        elif elapsed_time > 5:
            reset_user_clicks(user_id)
        
        return False  # يمكن المتابعة بشكل طبيعي
        
    except Exception as e:
        logger.error(f"Error in check_user_ban_and_track_clicks: {e}")
        return False  # في حالة الخطأ، نسمح بالمتابعة

# متغير عام لتتبع الإشعارات المعلقة
pending_unban_notifications = []

async def process_pending_unban_notifications(application):
    """معالجة الإشعارات المعلقة لرفع الحظر"""
    global pending_unban_notifications
    
    if not pending_unban_notifications:
        return
    
    notifications_to_process = pending_unban_notifications.copy()
    pending_unban_notifications.clear()
    
    for user_id in notifications_to_process:
        try:
            # الحصول على معلومات المستخدم
            user_result = db.execute_query("SELECT username FROM users WHERE user_id = ?", (user_id,))
            username = user_result[0][0] if user_result and user_result[0][0] else ""
            
            # إشعار المستخدم
            try:
                await notify_user_unban(application, user_id)
            except Exception as e:
                logger.error(f"Failed to notify user {user_id} about unban: {e}")
            
            # إشعار الآدمن
            try:
                await notify_admin_unban(application, user_id, username)
            except Exception as e:
                logger.error(f"Failed to notify admin about user {user_id} unban: {e}")
                
        except Exception as e:
            logger.error(f"Error processing unban notification for user {user_id}: {e}")

async def check_expired_bans_periodically(application):
    """فحص دوري للحظر المنتهي (كل 5 دقائق)"""
    from datetime import datetime
    
    try:
        # العثور على المستخدمين المحظورين الذين انتهت مدة حظرهم
        current_time = datetime.now().isoformat()
        expired_bans_query = """
            SELECT user_id FROM user_bans 
            WHERE is_banned = TRUE AND ban_end_time <= ?
        """
        expired_bans = db.execute_query(expired_bans_query, (current_time,))
        
        for row in expired_bans:
            user_id = row[0]
            
            # رفع الحظر
            was_lifted = lift_user_ban(user_id)
            if was_lifted:
                # إضافة إلى قائمة الإشعارات المعلقة
                global pending_unban_notifications
                if user_id not in pending_unban_notifications:
                    pending_unban_notifications.append(user_id)
                    logger.info(f"Added user {user_id} to unban notification queue")
        
        # معالجة الإشعارات المعلقة
        await process_pending_unban_notifications(application)
        
    except Exception as e:
        logger.error(f"Error in periodic ban check: {e}")

# إنشاء مدير قاعدة البيانات
db = DatabaseManager(DATABASE_FILE)

def get_current_price(price_type: str) -> str:
    """الحصول على السعر الحالي من قاعدة البيانات"""
    try:
        # للأسعار الخاصة، نحتاج للبحث في static_prices
        if price_type in ['weekly', 'datacenter']:
            static_prices = get_static_prices()
            if price_type == 'weekly':
                return static_prices.get('Weekly', '2.5')
            elif price_type == 'datacenter':
                return static_prices.get('Datacenter', '12')
        
        result = db.execute_query(f"SELECT value FROM settings WHERE key = '{price_type}_price'")
        if result:
            return result[0][0]
        else:
            # أسعار افتراضية
            defaults = {
                'verizon': '4',
                'att': '6', 
                'isp': '3',
                'weekly': '2.5'
            }
            return defaults.get(price_type, '3')
    except:
        defaults = {
            'verizon': '4',
            'att': '6',
            'isp': '3',
            'weekly': '2.5'
        }
        return defaults.get(price_type, '3')

def get_static_prices():
    """الحصول على جميع أسعار البروكسي الستاتيك من قاعدة البيانات"""
    try:
        static_prices_result = db.execute_query("SELECT value FROM settings WHERE key = 'static_prices'")
        if static_prices_result:
            static_prices_text = static_prices_result[0][0]
            if "," in static_prices_text:
                price_parts = static_prices_text.split(",")
                static_prices = {}
                for part in price_parts:
                    if ":" in part:
                        key, value = part.split(":", 1)
                        static_prices[key.strip()] = value.strip()
                return static_prices
            else:
                # إذا لم تكن في التنسيق الجديد، عودة للتنسيق الافتراضي
                return {
                    'ISP': '3',
                    'Res_1': '4',
                    'Res_2': '6',
                    'Daily': '0',
                    'Weekly': '2.5',
                    'Datacenter': '12'
                }
        else:
            # قيم افتراضية إذا لم توجد في قاعدة البيانات
            return {
                'ISP': '3',
                'Res_1': '4',
                'Res_2': '6',
                'Daily': '0',
                'Weekly': '2.5',
                'Datacenter': '12'
            }
    except:
        # في حالة الخطأ، قيم افتراضية
        return {
            'ISP': '3',
            'Res_1': '4',
            'Res_2': '6',
            'Daily': '0',
            'Weekly': '2.5',
            'Datacenter': '12'
        }

def get_socks_prices():
    """الحصول على جميع أسعار بروكسي السوكس من قاعدة البيانات"""
    try:
        socks_prices_result = db.execute_query("SELECT value FROM settings WHERE key = 'socks_prices'")
        if socks_prices_result:
            socks_prices_text = socks_prices_result[0][0]
            if "," in socks_prices_text:
                price_parts = socks_prices_text.split(",")
                socks_prices = {}
                for part in price_parts:
                    if ":" in part:
                        key, value = part.split(":", 1)
                        socks_prices[key.strip()] = value.strip()
                return socks_prices
            else:
                return {
                    'single_proxy': socks_prices_text.strip(),
                    'double_proxy': str(float(socks_prices_text.strip()) * 1.8),
                    '5proxy': socks_prices_text.strip(),
                    '10proxy': '0.7'
                }
        else:
            return {
                'single_proxy': '0.15',
                'double_proxy': '0.25',
                '5proxy': '0.4',
                '10proxy': '0.7'
            }
    except:
        return {
            'single_proxy': '0.15',
            'double_proxy': '0.25',
            '5proxy': '0.4',
            '10proxy': '0.7'
        }

def get_detailed_proxy_type(proxy_type: str, static_type: str = "") -> str:
    """تحويل نوع البروكسي إلى وصف مفصل"""
    if proxy_type == 'static':
        if static_type == 'residential_verizon':
            return "ستاتيك ريزيدنتال Verizon"
        elif static_type == 'residential_crocker':
            return "ستاتيك ريزيدنتال Crocker"
        elif static_type == 'residential_att':
            return "ستاتيك ريزيدنتال"
        elif static_type == 'isp':
            return "ستاتيك ISP"
        elif static_type == 'daily':
            return "ستاتيك يومي"
        elif static_type == 'weekly':
            return "ستاتيك اسبوعي"
        elif static_type == 'verizon_weekly':
            return "ستاتيك أسبوعي"
        else:
            return "ستاتيك"
    elif proxy_type == 'socks':
        return "سوكس"
    elif proxy_type == 'http':
        return "HTTP"
    elif proxy_type == 'ستاتيك يومي':
        return "ستاتيك يومي"
    elif proxy_type == 'ستاتيك اسبوعي':
        return "ستاتيك اسبوعي"
    else:
        return proxy_type

def get_proxy_price(proxy_type: str, country: str = "", state: str = "", static_type: str = "") -> float:
    """حساب سعر البروكسي بناءً على النوع والدولة"""
    try:
        if proxy_type == 'static':
            # تحديد السعر بناءً على نوع الستاتيك الجديد
            if static_type == 'residential_verizon':
                verizon_price_result = db.execute_query("SELECT value FROM settings WHERE key = 'verizon_price'")
                if verizon_price_result:
                    return float(verizon_price_result[0][0])
                return 4.0  # سعر افتراضي
            elif static_type == 'residential_crocker':
                # سعر Crocker مثل Verizon = $4
                crocker_price_result = db.execute_query("SELECT value FROM settings WHERE key = 'verizon_price'")
                if crocker_price_result:
                    return float(crocker_price_result[0][0])
                return 4.0  # سعر افتراضي
            elif static_type == 'residential_att':
                att_price_result = db.execute_query("SELECT value FROM settings WHERE key = 'att_price'")
                if att_price_result:
                    return float(att_price_result[0][0])
                return 6.0  # سعر افتراضي
            elif static_type == 'isp':
                isp_price_result = db.execute_query("SELECT value FROM settings WHERE key = 'isp_price'")
                if isp_price_result:
                    return float(isp_price_result[0][0])
                return 3.0  # سعر افتراضي
            elif static_type == 'verizon_weekly':
                # السعر من إعدادات الستاتيك Weekly
                static_prices = get_static_prices()
                return float(static_prices.get('Weekly', '2.5'))
            else:
                # للتوافق مع النظام القديم
                static_prices_result = db.execute_query("SELECT value FROM settings WHERE key = 'static_prices'")
                if static_prices_result:
                    static_prices_text = static_prices_result[0][0]
                    if "," in static_prices_text:
                        price_parts = static_prices_text.split(",")
                        static_prices = {}
                        for part in price_parts:
                            if ":" in part:
                                key, value = part.split(":", 1)
                                static_prices[key.strip()] = float(value.strip())
                        # تحديد السعر بناءً على نوع الستاتيك
                        if "Crocker" in state or "crocker" in state.lower():
                            return static_prices.get('Crocker', 4.0)
                        elif "AT&T" in state or "att" in state.lower():
                            return static_prices.get('ATT', 6.0)
                        else:
                            return static_prices.get('ISP', 3.0)  # ISP Risk0 افتراضي
                    else:
                        return float(static_prices_text.strip())
            return 3.0  # سعر افتراضي للستاتيك
        
        elif proxy_type == 'socks':
            # تحميل أسعار السوكس من قاعدة البيانات
            socks_prices_result = db.execute_query("SELECT value FROM settings WHERE key = 'socks_prices'")
            if socks_prices_result:
                socks_prices_text = socks_prices_result[0][0]
                if "," in socks_prices_text:
                    price_parts = socks_prices_text.split(",")
                    socks_prices = {}
                    for part in price_parts:
                        if ":" in part:
                            key, value = part.split(":", 1)
                            socks_prices[key.strip()] = float(value.strip())
                    return socks_prices.get('5proxy', 0.4)  # افتراضي 5 بروكسيات
                else:
                    return float(socks_prices_text.strip())
            return 0.4  # سعر افتراضي للسوكس
        
        return 0.0
    except Exception as e:
        print(f"خطأ في حساب سعر البروكسي: {e}")
        return 3.0 if proxy_type == 'static' else 0.4

def load_saved_prices():
    """تحميل الأسعار المحفوظة من قاعدة البيانات عند بدء تشغيل البوت"""
    try:
        # تحميل أسعار الستاتيك
        static_prices_result = db.execute_query("SELECT value FROM settings WHERE key = 'static_prices'")
        if static_prices_result:
            static_prices_text = static_prices_result[0][0]
            try:
                if "," in static_prices_text:
                    price_parts = static_prices_text.split(",")
                    static_prices = {}
                    for part in price_parts:
                        if ":" in part:
                            key, value = part.split(":", 1)
                            static_prices[key.strip()] = value.strip()
                else:
                    static_prices = {
                        "ISP": static_prices_text.strip(),
                        "Crocker": static_prices_text.strip(), 
                        "ATT": static_prices_text.strip()
                    }
                
                # تحديث رسائل الستاتيك
                update_static_messages(static_prices)
                print(f"📊 تم تحميل أسعار الستاتيك: {static_prices}")
            except Exception as e:
                print(f"خطأ في تحليل أسعار الستاتيك: {e}")
        
        # تحميل أسعار السوكس
        socks_prices_result = db.execute_query("SELECT value FROM settings WHERE key = 'socks_prices'")
        if socks_prices_result:
            socks_prices_text = socks_prices_result[0][0]
            try:
                if "," in socks_prices_text:
                    price_parts = socks_prices_text.split(",")
                    socks_prices = {}
                    for part in price_parts:
                        if ":" in part:
                            key, value = part.split(":", 1)
                            socks_prices[key.strip()] = value.strip()
                else:
                    socks_prices = {
                        "5proxy": socks_prices_text.strip(),
                        "10proxy": "0.7"
                    }
                
                # تحديث رسائل السوكس
                update_socks_messages(socks_prices)
                print(f"📊 تم تحميل أسعار السوكس: {socks_prices}")
            except Exception as e:
                print(f"خطأ في تحليل أسعار السوكس: {e}")
        
        # تحميل قيمة الإحالة
        referral_amount_result = db.execute_query("SELECT value FROM settings WHERE key = 'referral_amount'")
        if referral_amount_result:
            referral_amount = float(referral_amount_result[0][0])
            print(f"💰 تم تحميل قيمة الإحالة: {referral_amount}$")
        
    except Exception as e:
        print(f"خطأ في تحميل الأسعار المحفوظة: {e}")

def update_static_messages(static_prices):
    """تحديث رسائل البروكسي الستاتيك"""
    new_static_message_ar = f"""📦 باكج البروكسي الستاتيك

🔹 الأسعار المتوفرة:
• Static ISP: {static_prices.get('ISP', '3')}$
• Static Residential: {static_prices.get('Res_1', '4')}$ / {static_prices.get('Res_2', '6')}$
• Static Daily: {static_prices.get('Daily', '0')}$
• Static Weekly: {static_prices.get('Weekly', '0')}$

━━━━━━━━━━━━━━━
📋 بعد اختيار الخدمة:
✅ سيستقبل الأدمن طلبك
⚡ سنعالج الطلب ونرسل لك البروكسي
📬 ستصلك رسالة تأكيد عند الانتهاء

معرف الطلب: {{order_id}}"""

    new_static_message_en = f"""📦 Static Proxy Package

🔹 Available Prices:
• Static ISP: {static_prices.get('ISP', '3')}$
• Static Residential: {static_prices.get('Res_1', '4')}$ / {static_prices.get('Res_2', '6')}$
• Static Daily: {static_prices.get('Daily', '0')}$
• Static Weekly: {static_prices.get('Weekly', '0')}$

━━━━━━━━━━━━━━━
📋 After selecting service:
✅ Admin will receive your order
⚡ We'll process and send you the proxy
📬 You'll get confirmation when ready

Order ID: {{order_id}}"""

    # تحديث الرسائل في الكود
    MESSAGES['ar']['static_package'] = new_static_message_ar
    MESSAGES['en']['static_package'] = new_static_message_en

def update_socks_messages(socks_prices):
    """تحديث رسائل بروكسي السوكس"""
    new_socks_message_ar = f"""📦 باكج البروكسي السوكس
🌍 جميع دول العالم | اختيار الولاية والمزود

🔹 الأسعار المتوفرة:
• بروكسي واحد: {socks_prices.get('single_proxy', '0.15')}$
• بروكسيان اثنان: {socks_prices.get('double_proxy', '0.25')}$  
• باكج 5 بروكسيات مؤقتة: {socks_prices.get('5proxy', '0.4')}$
• باكج 10 بروكسيات مؤقتة: {socks_prices.get('10proxy', '0.7')}$

━━━━━━━━━━━━━━━
📋 بعد اختيار الخدمة:
✅ سيستقبل الأدمن طلبك
⚡ سنعالج الطلب ونرسل لك البروكسي
📬 ستصلك رسالة تأكيد عند الانتهاء

معرف الطلب: {{order_id}}"""

    new_socks_message_en = f"""📦 Socks Proxy Package
🌍 Worldwide | Choose State & Provider

🔹 Available Prices:
• One Proxy: {socks_prices.get('single_proxy', '0.15')}$
• Two Proxies: {socks_prices.get('double_proxy', '0.25')}$
• 5 Temporary Proxies Package: {socks_prices.get('5proxy', '0.4')}$
• 10 Temporary Proxies Package: {socks_prices.get('10proxy', '0.7')}$

━━━━━━━━━━━━━━━
📋 After selecting service:
✅ Admin will receive your order
⚡ We'll process and send you the proxy
📬 You'll get confirmation when ready

Order ID: {{order_id}}"""

    # تحديث الرسائل في الكود
    MESSAGES['ar']['socks_package'] = new_socks_message_ar
    MESSAGES['en']['socks_package'] = new_socks_message_en

def generate_order_id() -> str:
    """إنشاء معرف طلب فريد مكون من 16 خانة"""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=16))

def get_user_language(user_id: int) -> str:
    """الحصول على لغة المستخدم"""
    user = db.get_user(user_id)
    return user[4] if user else 'ar'  # اللغة في العمود الخامس

def get_referral_amount(order_amount: float = 0) -> float:
    """حساب قيمة الإحالة بناءً على نسبة مئوية من قيمة الطلب"""
    try:
        result = db.execute_query("SELECT value FROM settings WHERE key = 'referral_percentage'")
        percentage = float(result[0][0]) if result else 10.0  # نسبة افتراضية 10%
        return round((order_amount * percentage / 100), 2)
    except:
        return round((order_amount * 10.0 / 100), 2)  # نسبة افتراضية 10%

def get_referral_percentage() -> float:
    """الحصول على نسبة الإحالة المئوية من الإعدادات"""
    try:
        result = db.execute_query("SELECT value FROM settings WHERE key = 'referral_percentage'")
        return float(result[0][0]) if result else 10.0  # نسبة افتراضية 10%
    except:
        return 10.0  # نسبة افتراضية 10%

def clean_user_data_preserve_admin(context: ContextTypes.DEFAULT_TYPE) -> None:
    """تنظيف البيانات المؤقتة مع الحفاظ على حالة الأدمن"""
    # حفظ حالة الأدمن
    is_admin = context.user_data.get('is_admin', False)
    
    # تنظيف جميع البيانات
    context.user_data.clear()
    
    # استعادة حالة الأدمن
    if is_admin:
        context.user_data['is_admin'] = True

def create_main_user_keyboard(language: str) -> ReplyKeyboardMarkup:
    """إنشاء الكيبورد الرئيسي للمستخدم العادي (7 أزرار مرتبة بجمالية)"""
    keyboard = [
        [KeyboardButton(MESSAGES[language]['main_menu_buttons'][0])],  # طلب بروكسي ستاتيك
        [KeyboardButton(MESSAGES[language]['main_menu_buttons'][1])],  # طلب بروكسي سوكس
        [KeyboardButton(MESSAGES[language]['main_menu_buttons'][2]), KeyboardButton(MESSAGES[language]['main_menu_buttons'][3])],  # تجربة ستاتيك مجانا + إحالاتي
        [KeyboardButton(MESSAGES[language]['main_menu_buttons'][5]), KeyboardButton(MESSAGES[language]['main_menu_buttons'][4])],  # الإعدادات + تذكير بطلباتي
        [KeyboardButton(MESSAGES[language]['main_menu_buttons'][6])]   # خدماتنا
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def restore_admin_keyboard(context: ContextTypes.DEFAULT_TYPE, chat_id: int, message: str = "🔧 لوحة الأدمن جاهزة"):
    """إعادة تفعيل كيبورد الأدمن الرئيسي"""
    admin_keyboard = [
        [KeyboardButton("📋 إدارة الطلبات")],
        [KeyboardButton("💰 إدارة الأموال"), KeyboardButton("👥 الإحالات")],
        [KeyboardButton("📢 البث"), KeyboardButton("🔍 استعلام عن مستخدم")],
        [KeyboardButton("🌐 إدارة البروكسيات"), KeyboardButton("⚙️ الإعدادات")],
        [KeyboardButton("🚪 تسجيل الخروج")]
    ]
    admin_reply_markup = ReplyKeyboardMarkup(admin_keyboard, resize_keyboard=True)
    
    await context.bot.send_message(
        chat_id,
        message,
        reply_markup=admin_reply_markup
    )

def create_balance_keyboard(language: str) -> ReplyKeyboardMarkup:
    """إنشاء كيبورد قائمة الرصيد"""
    keyboard = [
        [KeyboardButton(MESSAGES[language]['balance_menu_buttons'][0])],  # شحن رصيد
        [KeyboardButton(MESSAGES[language]['balance_menu_buttons'][1])],  # رصيدي
        [KeyboardButton(MESSAGES[language]['balance_menu_buttons'][2])],  # الإحالات
        [KeyboardButton(MESSAGES[language]['balance_menu_buttons'][3])]   # العودة للقائمة الرئيسية
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def generate_transaction_number(transaction_type: str) -> str:
    """توليد رقم معاملة جديد"""
    # الحصول على آخر رقم معاملة من نفس النوع
    query = "SELECT MAX(id) FROM transactions WHERE transaction_type = ?"
    result = db.execute_query(query, (transaction_type,))
    
    last_id = 0
    if result and result[0][0]:
        last_id = result[0][0]
    
    # توليد الرقم الجديد
    new_id = last_id + 1
    
    if transaction_type == 'proxy':
        prefix = 'P'
    elif transaction_type == 'withdrawal':
        prefix = 'M'
    else:
        prefix = 'T'
    
    # تنسيق الرقم بـ 10 خانات
    transaction_number = f"{prefix}-{new_id:010d}"
    
    return transaction_number

def save_transaction(order_id: str, transaction_number: str, transaction_type: str, status: str = 'completed'):
    """حفظ بيانات المعاملة"""
    db.execute_query('''
        INSERT INTO transactions (order_id, transaction_number, transaction_type, status)
        VALUES (?, ?, ?, ?)
    ''', (order_id, transaction_number, transaction_type, status))

def update_order_status(order_id: str, status: str):
    """تحديث حالة الطلب"""
    if status == 'completed':
        db.execute_query('''
            UPDATE orders 
            SET status = 'completed', processed_at = CURRENT_TIMESTAMP 
            WHERE id = ?
        ''', (order_id,))
    elif status == 'failed':
        db.execute_query('''
            UPDATE orders 
            SET status = 'failed', processed_at = CURRENT_TIMESTAMP 
            WHERE id = ?
        ''', (order_id,))

async def handle_withdrawal_success(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالجة نجاح سحب الرصيد"""
    query = update.callback_query
    await query.answer()
    
    order_id = query.data.replace('withdrawal_success_', '')
    
    # توليد رقم المعاملة
    transaction_number = generate_transaction_number('withdrawal')
    save_transaction(order_id, transaction_number, 'withdrawal', 'completed')
    
    # تحديث حالة الطلب إلى مكتمل
    update_order_status(order_id, 'completed')
    
    # الحصول على بيانات المستخدم
    user_query = "SELECT user_id FROM orders WHERE id = ?"
    user_result = db.execute_query(user_query, (order_id,))
    
    if user_result:
        user_id = user_result[0][0]
        user = db.get_user(user_id)
        
        if user:
            user_language = get_user_language(user_id)
            withdrawal_amount = user[5]
            
            # تصفير رصيد المستخدم
            db.execute_query("UPDATE users SET referral_balance = 0 WHERE user_id = ?", (user_id,))
            
            # رسالة للمستخدم بلغته
            if user_language == 'ar':
                user_message = f"""✅ تم تسديد مكافأة الإحالة بنجاح!

💰 المبلغ: `{withdrawal_amount:.2f}$`
🆔 معرف الطلب: {order_id}
💳 رقم المعاملة: `{transaction_number}`

🎉 تم إيداع المبلغ بنجاح!"""
            else:
                user_message = f"""✅ Referral reward paid successfully!

💰 Amount: `{withdrawal_amount:.2f}$`
🆔 Order ID: {order_id}
💳 Transaction Number: `{transaction_number}`

🎉 Amount deposited successfully!"""
            
            await context.bot.send_message(user_id, user_message, parse_mode='Markdown')
            
            # إنشاء رسالة للأدمن مع زر فتح المحادثة
            keyboard = [
                [InlineKeyboardButton("💬 فتح محادثة مع المستخدم", url=f"tg://user?id={user_id}")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            admin_message = f"""✅ تم تسديد مكافأة الإحالة بنجاح!

👤 المستخدم: {user[2]} {user[3]}
📱 اسم المستخدم: @{user[1] or 'غير محدد'}
🆔 معرف المستخدم: `{user_id}`
💰 المبلغ المدفوع: `{withdrawal_amount:.2f}$`
🔗 معرف الطلب: `{order_id}`
💳 رقم المعاملة: `{transaction_number}`

📋 تم نقل الطلب إلى الطلبات المكتملة."""
            
            await query.edit_message_text(admin_message, reply_markup=reply_markup, parse_mode='Markdown')
            
            # إعادة تفعيل كيبورد الأدمن بعد فترة قصيرة
            import asyncio
            await asyncio.sleep(2)
            await restore_admin_keyboard(context, update.effective_chat.id)

async def handle_withdrawal_failed(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالجة فشل سحب الرصيد"""
    query = update.callback_query
    await query.answer()
    
    order_id = query.data.replace('withdrawal_failed_', '')
    
    # توليد رقم المعاملة
    transaction_number = generate_transaction_number('withdrawal')
    save_transaction(order_id, transaction_number, 'withdrawal', 'failed')
    
    # تحديث حالة الطلب إلى فاشل
    update_order_status(order_id, 'failed')
    
    # الحصول على بيانات المستخدم
    user_query = "SELECT user_id FROM orders WHERE id = ?"
    user_result = db.execute_query(user_query, (order_id,))
    
    if user_result:
        user_id = user_result[0][0]
        user = db.get_user(user_id)
        
        if user:
            user_language = get_user_language(user_id)
            withdrawal_amount = user[5]
            
            # رسالة للمستخدم
            if user_language == 'ar':
                user_message = f"""❌ فشلت عملية تسديد مكافأة الإحالة

💰 المبلغ: `{withdrawal_amount:.2f}$`
🆔 معرف الطلب: {order_id}
💳 رقم المعاملة: `{transaction_number}`

📞 يرجى التواصل مع الإدارة لمعرفة السبب."""
            else:
                user_message = f"""❌ Referral reward payment failed

💰 Amount: `{withdrawal_amount:.2f}$`
🆔 Order ID: {order_id}
💳 Transaction Number: `{transaction_number}`

📞 Please contact admin to know the reason."""
            
            await context.bot.send_message(user_id, user_message, parse_mode='Markdown')
            
            # رسالة للأدمن
            admin_message = f"""❌ فشلت عملية تسديد مكافأة الإحالة

👤 المستخدم: {user[2]} {user[3]}
🆔 معرف المستخدم: `{user_id}`
💰 المبلغ: `{withdrawal_amount:.2f}$`
🔗 معرف الطلب: `{order_id}`
💳 رقم المعاملة: `{transaction_number}`

📋 تم نقل الطلب إلى الطلبات الفاشلة."""
            
            await query.edit_message_text(admin_message, parse_mode='Markdown')
            
            # إعادة تفعيل كيبورد الأدمن بعد فترة قصيرة
            import asyncio
            await asyncio.sleep(2)
            await restore_admin_keyboard(context, update.effective_chat.id)

async def handle_approve_recharge(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """سؤال الآدمن عن قيمة الرصيد بالدولار قبل معالجة طلب الشحن"""
    try:
        query = update.callback_query
        await query.answer()
        
        # استخراج معرف الطلب من callback_data
        order_id = query.data.replace('approve_recharge_', '')
        
        # الحصول على بيانات الطلب
        order_query = "SELECT user_id, payment_amount, quantity FROM orders WHERE id = ? AND proxy_type = 'balance_recharge'"
        order_result = db.execute_query(order_query, (order_id,))
        
        if not order_result:
            await query.edit_message_text("❌ لم يتم العثور على طلب الشحن")
            return ConversationHandler.END
        
        user_id, user_amount, points_text = order_result[0]
        
        # حفظ بيانات الطلب في context للاستخدام لاحقاً
        context.user_data['recharge_order_id'] = order_id
        context.user_data['recharge_user_id'] = user_id
        context.user_data['recharge_user_amount'] = user_amount
        context.user_data['recharge_points_text'] = points_text
        
        # سؤال الآدمن عن قيمة الرصيد بالدولار
        try:
            await query.edit_message_text(
                f"""💰 **تحديد قيمة الرصيد**
                
🆔 معرف الطلب: `{order_id}`
💵 قيمة المستخدم: `${user_amount:.2f}`

❓ **ما هي قيمة الرصيد الفعلية بالدولار؟**

🔢 أدخل القيمة بالدولار (مثال: 25.50):""",
                parse_mode='Markdown'
            )
        except Exception as edit_error:
            # إذا فشل التعديل (مثلاً الرسالة صورة)، إرسال رسالة جديدة
            await context.bot.send_message(
                chat_id=query.message.chat_id,
                text=f"""💰 **تحديد قيمة الرصيد**
                
🆔 معرف الطلب: `{order_id}`
💵 قيمة المستخدم: `${user_amount:.2f}`

❓ **ما هي قيمة الرصيد الفعلية بالدولار؟**

🔢 أدخل القيمة بالدولار (مثال: 25.50):""",
                parse_mode='Markdown'
            )
        
        return ADMIN_RECHARGE_AMOUNT_INPUT
        
    except Exception as e:
        logger.error(f"Error in handle_approve_recharge: {e}")
        try:
            await query.edit_message_text("❌ حدث خطأ أثناء معالجة طلب الشحن")
        except Exception as edit_error:
            logger.error(f"Failed to edit message after error: {edit_error}")
        return ConversationHandler.END

async def handle_admin_recharge_amount_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """معالجة إدخال الآدمن لقيمة الرصيد"""
    try:
        admin_amount = float(update.message.text)
        user_amount = context.user_data.get('recharge_user_amount', 0.0)
        order_id = context.user_data.get('recharge_order_id')
        
        # حفظ قيمة الآدمن
        context.user_data['admin_recharge_amount'] = admin_amount
        
        if abs(admin_amount - user_amount) < 0.01:  # نفس القيمة (تقريباً)
            # المتابعة مباشرة بإتمام الشحن
            return await complete_recharge_approval(update, context, admin_amount)
        else:
            # الحصول على صورة إثبات الشحن
            recharge_proof_query = "SELECT proof_image FROM orders WHERE id = ?"
            proof_result = db.execute_query(recharge_proof_query, (order_id,))
            proof_image = proof_result[0][0] if proof_result and proof_result[0][0] else None
            
            # حساب النقاط المتوقعة لكل قيمة
            credit_price = db.get_credit_price()
            admin_points = admin_amount / credit_price
            user_points = user_amount / credit_price
            
            # عرض خيارات للآدمن
            keyboard = [
                [InlineKeyboardButton(f"💰 اعتماد قيمة الآدمن (${admin_amount:.2f})", callback_data=f"use_admin_amount_{order_id}")],
                [InlineKeyboardButton(f"👤 اعتماد قيمة الزبون (${user_amount:.2f})", callback_data=f"use_user_amount_{order_id}")],
                [InlineKeyboardButton("⏹️ إيقاف المعالجة", callback_data=f"stop_processing_{order_id}")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # إرسال الرسالة مع تفاصيل الاختلاف
            difference_message = f"""⚠️ **تنبيه: اختلاف في قيم الشحن**

🆔 معرف الطلب: `{order_id}`
👤 قيمة الزبون: `${user_amount:.2f}` (النقاط المتوقعة: {user_points:.2f})
💰 قيمة الآدمن: `${admin_amount:.2f}` (النقاط المتوقعة: {admin_points:.2f})
📊 الفرق: `${abs(admin_amount - user_amount):.2f}`

❓ **أي قيمة تريد اعتمادها؟**

📋 **خياراتك:**
💰 **قيمة الآدمن** - سيتم اعتماد `${admin_amount:.2f}` وإضافة `{admin_points:.2f}` نقطة
👤 **قيمة الزبون** - سيتم اعتماد `${user_amount:.2f}` وإضافة `{user_points:.2f}` نقطة  
⏹️ **إيقاف المعالجة** - لن يتم تصنيف الطلب كفاشل، سيبقى معلق للمراجعة لاحقاً"""

            # إرسال الرسالة أولاً
            await update.message.reply_text(
                difference_message,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
            # إرسال صورة إثبات الشحن إذا كانت متوفرة
            if proof_image:
                try:
                    await update.message.reply_photo(
                        photo=proof_image,
                        caption="📸 صورة إثبات الشحن المرفقة من الزبون"
                    )
                except Exception as photo_error:
                    logger.error(f"Error sending proof image: {photo_error}")
                    await update.message.reply_text("⚠️ لم يتم العثور على صورة إثبات الشحن أو حدث خطأ في عرضها")
            
            return ConversationHandler.END
            
    except ValueError:
        await update.message.reply_text(
            "❌ **قيمة غير صحيحة**\n\n🔢 أدخل رقماً صحيحاً (مثال: 25.50):",
            parse_mode='Markdown'
        )
        return ADMIN_RECHARGE_AMOUNT_INPUT
    except Exception as e:
        logger.error(f"Error in handle_admin_recharge_amount_input: {e}")
        await update.message.reply_text("❌ حدث خطأ، تم إلغاء العملية")
        return ConversationHandler.END

async def complete_recharge_approval(update: Update, context: ContextTypes.DEFAULT_TYPE, final_amount: float) -> int:
    """إتمام قبول طلب الشحن مع القيمة النهائية"""
    try:
        order_id = context.user_data.get('recharge_order_id')
        user_id = context.user_data.get('recharge_user_id')
        points_text = context.user_data.get('recharge_points_text', '')
        
        # حساب النقاط بناءً على القيمة النهائية
        credit_price = db.get_credit_price()
        expected_credits = final_amount / credit_price
        
        # الحصول على بيانات المستخدم
        user = db.get_user(user_id)
        if not user:
            await update.message.reply_text("❌ لم يتم العثور على بيانات المستخدم")
            return ConversationHandler.END
        
        user_language = get_user_language(user_id)
        
        # إضافة النقاط لرصيد المستخدم
        current_balance = db.get_user_balance(user_id)
        current_points = current_balance['charged_balance']
        new_points = current_points + expected_credits
        
        # استخدام add_points لإضافة النقاط وتسجيل المعاملة
        db.add_credits(user_id, expected_credits, 'recharge', order_id, f"شحن رصيد بقيمة ${final_amount:.2f}")
        
        # توليد رقم المعاملة
        transaction_number = generate_transaction_number('recharge')
        save_transaction(order_id, transaction_number, 'recharge', 'completed')
        
        # تحديث حالة الطلب إلى مكتمل
        update_order_status(order_id, 'completed')
        
        # إرسال رسالة للمستخدم
        if user_language == 'ar':
            user_message = f"""✅ تم قبول طلب شحن الرصيد بنجاح!

💰 المبلغ: ${final_amount:.2f}
💎 النقاط المضافة: {expected_credits:.2f} نقطة
💯 رصيدك الحالي: {new_points:.2f} نقطة
🆔 معرف الطلب: {order_id}
💳 رقم المعاملة: `{transaction_number}`

🎉 تم إضافة النقاط لحسابك بنجاح!"""
        else:
            user_message = f"""✅ Balance recharge request approved successfully!

💰 Amount: ${final_amount:.2f}
💎 Points Added: {expected_credits:.2f} points
💯 Current Balance: {new_points:.2f} points
🆔 Order ID: {order_id}
💳 Transaction Number: `{transaction_number}`

🎉 Points have been added to your account successfully!"""
        
        await context.bot.send_message(user_id, user_message, parse_mode='Markdown')
        
        # رسالة تأكيد للآدمن
        admin_message = f"""✅ تم إتمام شحن الرصيد بنجاح!

🆔 معرف الطلب: {order_id}
👤 المستخدم: {user[2]} {user[3] or ''}
💰 المبلغ النهائي: ${final_amount:.2f}
💎 النقاط المضافة: {expected_credits:.2f} نقطة
💳 رقم المعاملة: `{transaction_number}`"""
        
        await update.message.reply_text(admin_message, parse_mode='Markdown')
        
        # إعادة تفعيل كيبورد الأدمن
        await restore_admin_keyboard(context, update.effective_chat.id)
        
        return ConversationHandler.END
        
    except Exception as e:
        logger.error(f"Error in complete_recharge_approval: {e}")
        await update.message.reply_text("❌ حدث خطأ أثناء إتمام الشحن")
        return ConversationHandler.END

async def handle_recharge_amount_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالجة اختيار قيمة الشحن من الأزرار الثلاثة"""
    query = update.callback_query
    await query.answer()
    
    try:
        if query.data.startswith("use_admin_amount_"):
            order_id = query.data.replace("use_admin_amount_", "")
            admin_amount = context.user_data.get('admin_recharge_amount', 0.0)
            await complete_recharge_approval_with_amount(update, context, order_id, admin_amount, "admin")
            
        elif query.data.startswith("use_user_amount_"):
            order_id = query.data.replace("use_user_amount_", "")
            user_amount = context.user_data.get('recharge_user_amount', 0.0)
            await complete_recharge_approval_with_amount(update, context, order_id, user_amount, "user")
            
        elif query.data.startswith("stop_processing_"):
            order_id = query.data.replace("stop_processing_", "")
            await stop_recharge_processing(update, context, order_id)
            
    except Exception as e:
        logger.error(f"Error in handle_recharge_amount_choice: {e}")
        await query.edit_message_text("❌ حدث خطأ أثناء معالجة الاختيار")

async def complete_recharge_approval_with_amount(update: Update, context: ContextTypes.DEFAULT_TYPE, order_id: str, final_amount: float, amount_source: str) -> None:
    """إتمام قبول طلب الشحن مع القيمة المختارة"""
    try:
        query = update.callback_query
        
        # الحصول على بيانات الطلب
        order_query = "SELECT user_id, payment_amount FROM orders WHERE id = ? AND proxy_type = 'balance_recharge'"
        order_result = db.execute_query(order_query, (order_id,))
        
        if not order_result:
            await query.edit_message_text("❌ لم يتم العثور على طلب الشحن")
            return
        
        user_id = order_result[0][0]
        
        # حساب النقاط بناءً على القيمة النهائية
        credit_price = db.get_credit_price()
        expected_credits = final_amount / credit_price
        
        # الحصول على بيانات المستخدم
        user = db.get_user(user_id)
        if not user:
            await query.edit_message_text("❌ لم يتم العثور على بيانات المستخدم")
            return
        
        user_language = get_user_language(user_id)
        
        # إضافة النقاط لرصيد المستخدم
        current_balance = db.get_user_balance(user_id)
        current_points = current_balance['charged_balance']
        new_points = current_points + expected_credits
        
        # استخدام add_points لإضافة النقاط وتسجيل المعاملة
        source_text = "قيمة الآدمن" if amount_source == "admin" else "قيمة الزبون"
        db.add_credits(user_id, expected_credits, 'recharge', order_id, f"شحن رصيد بقيمة ${final_amount:.2f} ({source_text})")
        
        # توليد رقم المعاملة
        transaction_number = generate_transaction_number('recharge')
        save_transaction(order_id, transaction_number, 'recharge', 'completed')
        
        # تحديث حالة الطلب إلى مكتمل
        update_order_status(order_id, 'completed')
        
        # إرسال رسالة للمستخدم
        if user_language == 'ar':
            user_message = f"""✅ تم قبول طلب شحن الرصيد بنجاح!

💰 المبلغ: ${final_amount:.2f}
💎 النقاط المضافة: {expected_credits:.2f} نقطة
💯 رصيدك الحالي: {new_points:.2f} نقطة
🆔 معرف الطلب: {order_id}
💳 رقم المعاملة: `{transaction_number}`

🎉 تم إضافة النقاط لحسابك بنجاح!"""
        else:
            user_message = f"""✅ Balance recharge request approved successfully!

💰 Amount: ${final_amount:.2f}
💎 Points Added: {expected_credits:.2f} points
💯 Current Balance: {new_points:.2f} points
🆔 Order ID: {order_id}
💳 Transaction Number: `{transaction_number}`

🎉 Points have been added to your account successfully!"""
        
        await context.bot.send_message(user_id, user_message, parse_mode='Markdown')
        
        # رسالة تأكيد للآدمن
        admin_message = f"""✅ تم إتمام شحن الرصيد بنجاح!

🆔 معرف الطلب: {order_id}
👤 المستخدم: {user[2]} {user[3] or ''}
💰 المبلغ النهائي: ${final_amount:.2f} ({source_text})
💎 النقاط المضافة: {expected_credits:.2f} نقطة
💳 رقم المعاملة: `{transaction_number}`"""
        
        await query.edit_message_text(admin_message, parse_mode='Markdown')
        
        # إعادة تفعيل كيبورد الأدمن
        await restore_admin_keyboard(context, update.effective_chat.id)
        
    except Exception as e:
        logger.error(f"Error in complete_recharge_approval_with_amount: {e}")
        await query.edit_message_text("❌ حدث خطأ أثناء إتمام الشحن")

async def stop_recharge_processing(update: Update, context: ContextTypes.DEFAULT_TYPE, order_id: str) -> None:
    """إيقاف معالجة طلب الشحن دون تصنيفه كفاشل"""
    try:
        query = update.callback_query
        
        # الحصول على بيانات الطلب للعرض
        order_query = "SELECT user_id, payment_amount FROM orders WHERE id = ? AND proxy_type = 'balance_recharge'"
        order_result = db.execute_query(order_query, (order_id,))
        
        if order_result:
            user_id = order_result[0][0]
            user = db.get_user(user_id)
            user_name = f"{user[2]} {user[3] or ''}" if user else "غير معروف"
            
            stop_message = f"""⏹️ تم إيقاف معالجة طلب الشحن

🆔 معرف الطلب: {order_id}
👤 المستخدم: {user_name}
📊 حالة الطلب: معلق (للمراجعة اليدوية)

ℹ️ لم يتم تصنيف الطلب كفاشل، ويمكن معالجته لاحقاً من قائمة الطلبات المعلقة."""
        else:
            stop_message = f"""⏹️ تم إيقاف معالجة الطلب

🆔 معرف الطلب: {order_id}
📊 حالة الطلب: معلق (للمراجعة اليدوية)"""
        
        await query.edit_message_text(stop_message, parse_mode='Markdown')
        
        # إعادة تفعيل كيبورد الأدمن
        await restore_admin_keyboard(context, update.effective_chat.id)
        
    except Exception as e:
        logger.error(f"Error in stop_recharge_processing: {e}")
        await query.edit_message_text("❌ حدث خطأ أثناء إيقاف المعالجة")

async def handle_recharge_amount_choice_old(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالجة اختيار الآدمن لقيمة الرصيد"""
    try:
        query = update.callback_query
        await query.answer()
        
        if query.data.startswith("use_admin_amount_"):
            admin_amount = context.user_data.get('admin_recharge_amount', 0.0)
            await complete_recharge_approval(update, context, admin_amount)
        elif query.data.startswith("use_user_amount_"):
            user_amount = context.user_data.get('recharge_user_amount', 0.0)
            await complete_recharge_approval(update, context, user_amount)
        elif query.data.startswith("stop_processing_"):
            order_id = context.user_data.get('recharge_order_id')
            await query.edit_message_text(
                f"⏹️ تم إيقاف معالجة طلب الشحن\n\n🆔 معرف الطلب: `{order_id}`\n\n📝 يمكن العودة لمعالجته لاحقاً من قائمة الطلبات المعلقة.",
                parse_mode='Markdown'
            )
            await restore_admin_keyboard(context, update.effective_chat.id)
        
    except Exception as e:
        logger.error(f"Error in handle_recharge_amount_choice: {e}")
        await query.edit_message_text("❌ حدث خطأ أثناء معالجة الاختيار")
        await restore_admin_keyboard(context, update.effective_chat.id)

async def handle_reject_recharge(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالجة رفض طلب شحن الرصيد"""
    try:
        query = update.callback_query
        await query.answer()
        
        # استخراج معرف الطلب من callback_data
        order_id = query.data.replace('reject_recharge_', '')
        
        # الحصول على بيانات الطلب
        order_query = "SELECT user_id, payment_amount, quantity FROM orders WHERE id = ? AND proxy_type = 'balance_recharge'"
        order_result = db.execute_query(order_query, (order_id,))
        
        if not order_result:
            await query.edit_message_text("❌ لم يتم العثور على طلب الشحن")
            return
        
        user_id, amount, points_text = order_result[0]
        expected_credits = float(points_text.replace(' points', ''))
        
        # الحصول على بيانات المستخدم
        user = db.get_user(user_id)
        if not user:
            await query.edit_message_text("❌ لم يتم العثور على بيانات المستخدم")
            return
        
        user_language = get_user_language(user_id)
        
        # توليد رقم المعاملة
        transaction_number = generate_transaction_number('recharge')
        save_transaction(order_id, transaction_number, 'recharge', 'failed')
        
        # تحديث حالة الطلب إلى مرفوض
        update_order_status(order_id, 'failed')
        
        # إرسال رسالة للمستخدم
        if user_language == 'ar':
            user_message = f"""❌ تم رفض طلب شحن الرصيد

💰 المبلغ: ${amount:.2f}
💎 النقاط المطلوبة: {expected_credits:.2f} نقطة
🆔 معرف الطلب: {order_id}
💳 رقم المعاملة: `{transaction_number}`

📞 يرجى التواصل مع الإدارة لمعرفة سبب الرفض وتصحيح المشكلة."""
        else:
            user_message = f"""❌ Balance recharge request rejected

💰 Amount: ${amount:.2f}
💎 Requested Points: {expected_credits:.2f} points
🆔 Order ID: {order_id}
💳 Transaction Number: `{transaction_number}`

📞 Please contact admin to know the reason for rejection and fix the issue."""
        
        await context.bot.send_message(user_id, user_message, parse_mode='Markdown')
        
        # الحصول على بيانات إضافية للعرض المتسق
        order_query_details = """SELECT payment_method, created_at FROM orders WHERE id = ? AND proxy_type = 'balance_recharge'"""
        order_details = db.execute_query(order_query_details, (order_id,))
        payment_method = order_details[0][0] if order_details else ''
        created_at = order_details[0][1] if order_details else 'غير محدد'
        
        # معالجة طريقة الدفع للعرض
        payment_method_display = {
            'shamcash': 'شام كاش 💳',
            'syriatel': 'سيرياتيل كاش 💳',
            'coinex': 'Coinex 🪙',
            'binance': 'Binance 🪙',
            'payeer': 'Payeer 🪙'
        }.get(payment_method or '', payment_method or 'غير محدد')
        
        # تحديث رسالة الآدمن لتصبح رسالة فشل مع زر فتح المحادثة فقط
        admin_message = f"""📋 تفاصيل طلب شحن الرصيد

🆔 معرف الطلب: {order_id}
📊 حالة الطلب: ❌ مرفوض

━━━━━━━━━━━━━━━
👤 بيانات المستخدم:
📝 الاسم: {user[2]} {user[3] or ''}
📱 اسم المستخدم: @{user[1] or 'غير محدد'}
🆔 المعرف: {user_id}

━━━━━━━━━━━━━━━
💰 تفاصيل الطلب:
💵 المبلغ: ${amount:.2f}
💎 النقاط المتوقعة: {expected_credits:.2f} نقطة
💳 طريقة الدفع: {payment_method_display}
📅 وقت الطلب: {created_at}

━━━━━━━━━━━━━━━
📸 إثبات الدفع: ✅ مرفق"""
        
        # إنشاء زر فتح المحادثة فقط
        keyboard = [[InlineKeyboardButton("💬 فتح محادثة مع المستخدم", url=f"tg://user?id={user_id}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # محاولة تعديل الرسالة (نص أو caption للصور)
        try:
            # محاولة تعديل النص أولاً
            await query.edit_message_text(admin_message, reply_markup=reply_markup, parse_mode='Markdown')
        except Exception as text_edit_error:
            if "There is no text in the message to edit" in str(text_edit_error):
                # إذا كانت الرسالة تحتوي على صورة، استخدم editMessageCaption
                try:
                    await query.edit_message_caption(caption=admin_message, reply_markup=reply_markup, parse_mode='Markdown')
                except Exception as caption_edit_error:
                    logger.error(f"Failed to edit message caption in reject: {caption_edit_error}")
                    # إذا فشل تعديل العنوان أيضاً، احذف الرسالة وأرسل رسالة جديدة
                    try:
                        await query.delete_message()
                        await context.bot.send_message(
                            chat_id=update.effective_chat.id,
                            text=admin_message,
                            reply_markup=reply_markup,
                            parse_mode='Markdown'
                        )
                    except Exception as new_message_error:
                        logger.error(f"Failed to send new message in reject: {new_message_error}")
            else:
                logger.error(f"Failed to edit message text in reject: {text_edit_error}")
                raise
        
        # إعادة تفعيل كيبورد الأدمن
        await restore_admin_keyboard(context, update.effective_chat.id)
        
    except Exception as e:
        logger.error(f"Error in handle_reject_recharge: {e}")
        try:
            await query.edit_message_text("❌ حدث خطأ أثناء معالجة طلب الشحن")
        except Exception as edit_error:
            logger.error(f"Failed to edit message after error: {edit_error}")
        await restore_admin_keyboard(context, update.effective_chat.id)

async def handle_view_recharge_details_with_id(update: Update, context: ContextTypes.DEFAULT_TYPE, order_id: str, answered: bool = False) -> None:
    """معالجة عرض تفاصيل طلب شحن الرصيد مع معرف الطلب المحدد"""
    try:
        query = update.callback_query
        if not answered:
            await query.answer()
        
        # الحصول على بيانات الطلب
        order_query = """SELECT user_id, payment_amount, quantity, payment_method, payment_proof, created_at, status 
                        FROM orders WHERE id = ? AND proxy_type = 'balance_recharge'"""
        order_result = db.execute_query(order_query, (order_id,))
        
        if not order_result:
            await query.edit_message_text("❌ لم يتم العثور على طلب الشحن")
            return
        
        order_data = order_result[0]
        if len(order_data) < 7:
            await query.edit_message_text("❌ بيانات طلب الشحن غير كاملة")
            return
        
        user_id, amount, points_text, payment_method, payment_proof, created_at, status = order_data
        expected_credits = float(str(points_text).replace(' points', '')) if points_text else 0.0
        
        # الحصول على بيانات المستخدم
        user = db.get_user(user_id)
        if not user:
            await query.edit_message_text("❌ لم يتم العثور على بيانات المستخدم")
            return
        
        # معالجة طريقة الدفع للعرض
        payment_method_display = {
            'shamcash': 'شام كاش 💳',
            'syriatel': 'سيرياتيل كاش 💳',
            'coinex': 'Coinex 🪙',
            'binance': 'Binance 🪙',
            'payeer': 'Payeer 🪙'
        }.get(payment_method or '', payment_method or 'غير محدد')
        
        # معالجة حالة الطلب
        status_display = {
            'pending': '⏳ معلق',
            'completed': '✅ مكتمل',
            'failed': '❌ مرفوض'
        }.get(status, status)
        
        # تحقق من حالة الطلب لعرض رسالة مناسبة
        if status == 'completed':
            # رسالة نجاح للطلبات المكتملة مع زر فتح المحادثة فقط
            success_message = f"""📋 تفاصيل طلب شحن الرصيد

🆔 معرف الطلب: {order_id}
📊 حالة الطلب: ✅ مكتمل

━━━━━━━━━━━━━━━
👤 بيانات المستخدم:
📝 الاسم: {user[2]} {user[3] or ''}
📱 اسم المستخدم: @{user[1] or 'غير محدد'}
🆔 المعرف: {user_id}

━━━━━━━━━━━━━━━
💰 تفاصيل الطلب:
💵 المبلغ: ${amount:.2f}
💎 النقاط المتوقعة: {expected_credits:.2f} نقطة
💳 طريقة الدفع: {payment_method_display}
📅 وقت الطلب: {created_at}

━━━━━━━━━━━━━━━
📸 إثبات الدفع: ✅ مرفق"""
            
            # إنشاء زر فتح المحادثة فقط
            keyboard = [[InlineKeyboardButton("💬 فتح محادثة مع المستخدم", url=f"tg://user?id={user_id}")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # عرض رسالة النجاح مع زر فتح المحادثة
            await query.edit_message_text(success_message, reply_markup=reply_markup, parse_mode='Markdown')
            return
            
        elif status == 'failed':
            # رسالة رفض للطلبات المرفوضة مع زر فتح المحادثة فقط
            reject_message = f"""📋 تفاصيل طلب شحن الرصيد

🆔 معرف الطلب: {order_id}
📊 حالة الطلب: ❌ مرفوض

━━━━━━━━━━━━━━━
👤 بيانات المستخدم:
📝 الاسم: {user[2]} {user[3] or ''}
📱 اسم المستخدم: @{user[1] or 'غير محدد'}
🆔 المعرف: {user_id}

━━━━━━━━━━━━━━━
💰 تفاصيل الطلب:
💵 المبلغ: ${amount:.2f}
💎 النقاط المطلوبة: {expected_credits:.2f} نقطة
💳 طريقة الدفع: {payment_method_display}
📅 وقت الطلب: {created_at}

━━━━━━━━━━━━━━━
📸 إثبات الدفع: ✅ مرفق"""
            
            # إنشاء زر فتح المحادثة فقط
            keyboard = [[InlineKeyboardButton("💬 فتح محادثة مع المستخدم", url=f"tg://user?id={user_id}")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # عرض رسالة الرفض مع زر فتح المحادثة
            await query.edit_message_text(reject_message, reply_markup=reply_markup, parse_mode='Markdown')
            return
        
        # للطلبات المعلقة فقط - عرض التفاصيل مع الأزرار
        details_message = f"""📋 تفاصيل طلب شحن الرصيد

🆔 معرف الطلب: {order_id}
📊 حالة الطلب: {status_display}

━━━━━━━━━━━━━━━
👤 بيانات المستخدم:
📝 الاسم: {user[2]} {user[3] or ''}
📱 اسم المستخدم: @{user[1] or 'غير محدد'}
🆔 المعرف: `{user_id}`

━━━━━━━━━━━━━━━
💰 تفاصيل الطلب:
💵 المبلغ: ${amount:.2f}
💎 النقاط المتوقعة: {expected_credits:.2f} نقطة
💳 طريقة الدفع: {payment_method_display}
📅 وقت الطلب: {created_at}

━━━━━━━━━━━━━━━
📸 إثبات الدفع: {'✅ مرفق' if payment_proof else '❌ غير متوفر'}"""
        
        # إنشاء الأزرار للطلبات المعلقة فقط
        keyboard = [
            [
                InlineKeyboardButton("✅ قبول الطلب", callback_data=f"approve_recharge_{order_id}"),
                InlineKeyboardButton("❌ رفض الطلب", callback_data=f"reject_recharge_{order_id}")
            ],
            [
                InlineKeyboardButton("💬 فتح محادثة مع المستخدم", url=f"tg://user?id={user_id}")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # إرسال التفاصيل مع إثبات الدفع إذا كان متوفراً
        if payment_proof and payment_proof.startswith("photo:"):
            file_id = payment_proof.replace("photo:", "")
            
            # إرسال صورة إثبات الدفع مع التفاصيل وأزرار التحكم
            loading_message = await query.edit_message_text("📋 جاري تحميل تفاصيل الطلب...")
            
            await context.bot.send_photo(
                query.message.chat_id,
                photo=file_id,
                caption=details_message,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
            # حذف رسالة التحميل لتجنب الفوضى في المحادثة
            try:
                await context.bot.delete_message(
                    chat_id=query.message.chat_id,
                    message_id=loading_message.message_id
                )
            except Exception as delete_error:
                logger.warning(f"Could not delete loading message: {delete_error}")
        else:
            # إرسال التفاصيل فقط بدون صورة
            await query.edit_message_text(details_message, reply_markup=reply_markup, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Error in handle_view_recharge_details_with_id: {e}")
        await query.edit_message_text("❌ حدث خطأ أثناء عرض تفاصيل طلب الشحن")

async def handle_view_recharge_details(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالجة عرض تفاصيل طلب شحن الرصيد"""
    try:
        query = update.callback_query
        await query.answer()
        
        # استخراج معرف الطلب من callback_data
        order_id = query.data.replace('view_recharge_', '')
        
        # استدعاء الدالة المساعدة مع معرف الطلب
        await handle_view_recharge_details_with_id(update, context, order_id, answered=True)
        
    except Exception as e:
        logger.error(f"Error in handle_view_recharge_details: {e}")
        await query.edit_message_text("❌ حدث خطأ أثناء عرض تفاصيل طلب الشحن")

async def change_admin_password(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """بدء عملية تغيير كلمة مرور الأدمن"""
    user_language = get_user_language(update.effective_user.id)
    
    if user_language == 'ar':
        message = "🔐 تغيير كلمة المرور\n\nيرجى إدخال كلمة المرور الحالية أولاً:"
    else:
        message = "🔐 Change Password\n\nPlease enter current password first:"
    
    back_text = "🔙 رجوع" if user_language == 'ar' else "🔙 Back"
    keyboard = [[InlineKeyboardButton(back_text, callback_data="cancel_password_change")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(message, reply_markup=reply_markup)
    context.user_data['password_change_step'] = 'current'
    return ADMIN_LOGIN

async def handle_password_change(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """معالجة تغيير كلمة المرور"""
    global ADMIN_PASSWORD
    step = context.user_data.get('password_change_step', 'current')
    user_language = get_user_language(update.effective_user.id)
    
    if step == 'current':
        # التحقق من كلمة المرور الحالية
        if update.message.text == ADMIN_PASSWORD:
            # حذف رسالة كلمة المرور الحالية من المحادثة لأسباب أمنية
            try:
                await context.bot.delete_message(
                    chat_id=update.effective_chat.id,
                    message_id=update.message.message_id
                )
            except Exception as e:
                print(f"تعذر حذف رسالة كلمة المرور الحالية: {e}")
            
            context.user_data['password_change_step'] = 'new'
            if user_language == 'ar':
                keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data="cancel_password_change")]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await update.message.reply_text("✅ كلمة المرور صحيحة\n\nيرجى إدخال كلمة المرور الجديدة:", reply_markup=reply_markup)
            else:
                keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="cancel_password_change")]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await update.message.reply_text("✅ Password correct\n\nPlease enter new password:", reply_markup=reply_markup)
            return ADMIN_LOGIN
        else:
            if user_language == 'ar':
                await update.message.reply_text("❌ كلمة المرور غير صحيحة!")
            else:
                await update.message.reply_text("❌ Invalid password!")
            context.user_data.pop('password_change_step', None)
            return ConversationHandler.END
    
    elif step == 'new':
        # تحديث كلمة المرور
        new_password = update.message.text
        ADMIN_PASSWORD = new_password
        
        # حذف رسالة كلمة المرور الجديدة من المحادثة لأسباب أمنية
        try:
            await context.bot.delete_message(
                chat_id=update.effective_chat.id,
                message_id=update.message.message_id
            )
        except Exception as e:
            print(f"تعذر حذف رسالة كلمة المرور الجديدة: {e}")
        
        # حفظ كلمة المرور الجديدة في قاعدة البيانات
        db.execute_query(
            "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
            ("admin_password", new_password)
        )
        
        if user_language == 'ar':
            await update.message.reply_text("✅ تم تغيير كلمة المرور بنجاح!")
        else:
            await update.message.reply_text("✅ Password changed successfully!")
        
        context.user_data.pop('password_change_step', None)
        return ConversationHandler.END
    
    return ConversationHandler.END

async def handle_cancel_password_change(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """معالجة إلغاء تغيير كلمة المرور"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    user_language = get_user_language(user_id)
    is_admin = context.user_data.get('is_admin', False)
    
    if user_language == 'ar':
        await query.edit_message_text("❌ تم إلغاء تغيير كلمة المرور")
    else:
        await query.edit_message_text("❌ Password change cancelled")
    
    # تنظيف البيانات المؤقتة
    context.user_data.pop('password_change_step', None)
    
    # إعادة الكيبورد المناسب
    if is_admin:
        await restore_admin_keyboard(context, user_id, "🔧 لوحة الأدمن جاهزة")
    else:
        # إعادة الكيبورد الرئيسي للمستخدم العادي
        await start(query, context)
    
    return ConversationHandler.END

def validate_ip_address(ip: str) -> bool:
    """التحقق من صحة عنوان IP"""
    import re
    # نمط للتحقق من الهيكل: 1-3 أرقام.1-3 أرقام.1-3 أرقام.1-3 أرقام
    pattern = r'^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$'
    return bool(re.match(pattern, ip))

def validate_port(port: str) -> bool:
    """التحقق من صحة رقم البورت"""
    # التحقق من أن المدخل رقمي وطوله 1-6 أرقام
    if not port.isdigit():
        return False
    
    port_int = int(port)
    # التحقق من أن الرقم بين 1 و 999999 (6 أرقام كحد أقصى)
    return 1 <= port_int <= 999999

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """أمر المساعدة"""
    user_id = update.effective_user.id
    language = get_user_language(user_id)
    
    if language == 'ar':
        message = "ℹ️ للتواصل مع الدعم و الآدمن على المعرف التالي @Static_support \n @Socks_support"
    else:
        message = "ℹ️ For support and admin contact: @Static_support \n @Socks_support"
    
    await update.message.reply_text(message)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """أمر البداية - إلغاء جميع العمليات المعلقة وإعادة تعيين الحالة"""
    user = update.effective_user
    
    # تنظيف جميع البيانات المؤقتة والعمليات المعلقة
    context.user_data.clear()
    
    # التحقق من وجود المستخدم مسبقاً
    existing_user = db.get_user(user.id)
    is_new_user = existing_user is None
    
    # إضافة المستخدم إلى قاعدة البيانات
    referred_by = None
    if context.args and is_new_user:
        try:
            referred_by = int(context.args[0])
            # التأكد من أن المحيل موجود
            referrer = db.get_user(referred_by)
            if not referrer:
                referred_by = None
        except ValueError:
            pass
    
    # تحديد اللغة تلقائياً للمستخدمين الجدد
    auto_language = 'ar'  # افتراضي
    if is_new_user and hasattr(user, 'language_code') and user.language_code:
        # إذا كانت اللغة عربية، استخدم العربية، وإلا استخدم الإنجليزية
        if user.language_code.startswith('ar'):
            auto_language = 'ar'
        else:
            auto_language = 'en'
    
    db.add_user(user.id, user.username, user.first_name, user.last_name, referred_by, auto_language if is_new_user else None)
    
    # إضافة مكافأة الإحالة للمحيل
    if referred_by and is_new_user:
        await add_referral_bonus(referred_by, user.id)
        
        # إشعار المحيل (بدون كشف الهوية)
        try:
            await context.bot.send_message(
                referred_by,
                f"🎉 تهانينا! انضم مستخدم جديد عبر رابط الإحالة الخاص بك.\n💰 ستحصل على {get_referral_percentage()}% من قيمة كل عملية شراء يقوم بها!",
                parse_mode='Markdown'
            )
        except:
            pass  # في حالة عدم إمكانية إرسال الرسالة
        
        # إشعار الأدمن بانضمام عضو جديد عبر الإحالة
        await send_referral_notification(context, referred_by, user)
    
    db.log_action(user.id, "start_command")
    
    language = get_user_language(user.id)
    
    # رسالة ترحيب للمستخدمين الجدد
    if is_new_user:
        welcome_message = MESSAGES[language]['welcome']
        if referred_by:
            welcome_message += f"\n\n🎁 مرحباً بك! لقد انضممت عبر رابط إحالة وحصل صديقك على مكافأة!"
    else:
        welcome_message = f"مرحباً بعودتك {user.first_name}! 😊\n\n" + MESSAGES[language]['welcome']
    
    # إنشاء الأزرار الرئيسية (6 أزرار كاملة)
    reply_markup = create_main_user_keyboard(language)
    
    await update.message.reply_text(
        welcome_message,
        reply_markup=reply_markup
    )
    
    # إرجاع ConversationHandler.END للتأكد من إنهاء أي محادثة نشطة
    return ConversationHandler.END

async def admin_login(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """تسجيل دخول الأدمن"""
    language = get_user_language(update.effective_user.id)
    await update.message.reply_text(MESSAGES[language]['admin_login_prompt'])
    return ADMIN_LOGIN

async def handle_admin_password(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """التحقق من كلمة مرور الأدمن"""
    global ADMIN_PASSWORD, ACTIVE_ADMINS
    if update.message.text == ADMIN_PASSWORD:
        user_id = update.effective_user.id
        context.user_data['is_admin'] = True
        
        # إضافة الآدمن لقائمة الآدمن النشطين إذا لم يكن موجوداً
        if user_id not in ACTIVE_ADMINS:
            ACTIVE_ADMINS.append(user_id)
        
        # تسجيل تسجيل دخول الآدمن
        try:
            db.log_action(user_id, "admin_login_success")
        except Exception as log_error:
            logger.error(f"Error logging admin login: {log_error}")
        
        # حذف رسالة كلمة المرور من المحادثة لأسباب أمنية
        try:
            await context.bot.delete_message(
                chat_id=update.effective_chat.id,
                message_id=update.message.message_id
            )
        except Exception as e:
            print(f"تعذر حذف رسالة كلمة المرور: {e}")
        
        # لوحة مفاتيح عادية للأدمن
        keyboard = [
            [KeyboardButton("📋 إدارة الطلبات")],
            [KeyboardButton("💰 إدارة الأموال"), KeyboardButton("👥 الإحالات")],
            [KeyboardButton("📢 البث"), KeyboardButton("🔍 استعلام عن مستخدم")],
            [KeyboardButton("🌐 إدارة البروكسيات"), KeyboardButton("⚙️ الإعدادات")],
            [KeyboardButton("🚪 تسجيل الخروج")]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        
        await update.message.reply_text(
            "🔧 مرحباً بك في لوحة الأدمن\nاختر الخدمة المطلوبة:",
            reply_markup=reply_markup
        )
        return ConversationHandler.END  # إنهاء المحادثة لتمكين إعادة الاستخدام
    else:
        await update.message.reply_text("كلمة المرور غير صحيحة!")
        return ConversationHandler.END

async def handle_static_proxy_request(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالجة طلب البروكسي الستاتيك"""
    user_id = update.effective_user.id
    language = get_user_language(user_id)
    
    # التحقق من حالة خدمات الستاتيك قبل المتابعة
    if not await check_service_availability('static', update, context, language):
        return
    
    # حفظ نوع البروكسي فقط بدون إنشاء معرف الطلب
    context.user_data['proxy_type'] = 'static'
    
    db.log_action(user_id, "static_proxy_request_started")
    
    # الحصول على الأسعار أولاً
    verizon_price = get_current_price('verizon')
    att_price = get_current_price('att')
    isp_price = get_current_price('isp')
    weekly_price = get_current_price('weekly')
    daily_price = get_current_price('daily')
    
    # عرض رسالة الحزمة مع الأسعار الفعلية
    if language == 'ar':
        replacement_text = 'سيتم إنشاء معرف الطلب'
    else:
        replacement_text = 'Order ID will be generated'
    
    package_message = MESSAGES[language]['static_package'].format(
        isp_price=isp_price,
        res_price=verizon_price,
        daily_price=daily_price,
        weekly_price=weekly_price,
        order_id=''
    ).replace('معرف الطلب: ' if language == 'ar' else 'Order ID: ', replacement_text)
    await update.message.reply_text(package_message)
    
    # الحصول على سعر داتا سينتر
    datacenter_price = get_current_price('datacenter')
    
    if language == 'ar':
        keyboard = [
            [InlineKeyboardButton(f"📅 ستاتيك أسبوعي ({weekly_price}$)", callback_data="verizon_weekly")],
            [InlineKeyboardButton(f"🌐 ISP ({isp_price}$)", callback_data="quantity_isp_static")],
            [InlineKeyboardButton(f"🏠 ريزيدنتال ({verizon_price}$)", callback_data="residential_4_dollar")],
            [InlineKeyboardButton(f"🏢 ريزيدنتال ({att_price}$)", callback_data="quantity_package_static")],
            [InlineKeyboardButton(f"🔧 بروكسي داتا سينتر ({datacenter_price}$)", callback_data="datacenter_proxy")],
            [InlineKeyboardButton("📅 ستاتيك يومي", callback_data="static_daily")],
            [InlineKeyboardButton("🔙 رجوع", callback_data="cancel_user_proxy_request")]
        ]
        quantity_text = "اختر نوع البروكسي المطلوب:"
    else:
        keyboard = [
            [InlineKeyboardButton(f"📅 Static Weekly ({weekly_price}$)", callback_data="verizon_weekly")],
            [InlineKeyboardButton(f"🌐 ISP ({isp_price}$)", callback_data="quantity_isp_static")],
            [InlineKeyboardButton(f"🏠 Residential ({verizon_price}$)", callback_data="residential_4_dollar")],
            [InlineKeyboardButton(f"🏢 Residential ({att_price}$)", callback_data="quantity_package_static")],
            [InlineKeyboardButton(f"🔧 Datacenter Proxy ({datacenter_price}$)", callback_data="datacenter_proxy")],
            [InlineKeyboardButton("📅 Static Daily", callback_data="static_daily")],
            [InlineKeyboardButton("🔙 Back", callback_data="cancel_user_proxy_request")]
        ]
        quantity_text = "Choose the proxy type required:"
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(quantity_text, reply_markup=reply_markup)
    context.user_data['proxy_type'] = 'static'
    return

async def handle_socks_proxy_request(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالجة طلب بروكسي السوكس"""
    user_id = update.effective_user.id
    language = get_user_language(user_id)
    
    # التحقق من حالة خدمات السوكس قبل المتابعة
    if not await check_service_availability('socks', update, context, language):
        return
    
    # حفظ نوع البروكسي فقط بدون إنشاء معرف الطلب
    context.user_data['proxy_type'] = 'socks'
    
    db.log_action(user_id, "socks_proxy_request_started")
    
    # الحصول على أسعار السوكس الديناميكية أولاً
    socks_prices = get_socks_prices()
    single_price = socks_prices.get('single_proxy', '0.15')
    double_price = socks_prices.get('double_proxy', '0.25')
    package5_price = socks_prices.get('5proxy', '0.4')
    package10_price = socks_prices.get('10proxy', '0.7')
    
    # عرض رسالة الحزمة مع الأسعار الفعلية
    if language == 'ar':
        replacement_text = 'سيتم إنشاء معرف الطلب'
    else:
        replacement_text = 'Order ID will be generated'
    
    package_message = MESSAGES[language]['socks_package'].format(
        single_price=single_price,
        double_price=double_price,
        five_price=package5_price,
        ten_price=package10_price,
        order_id=''
    ).replace('معرف الطلب: ' if language == 'ar' else 'Order ID: ', replacement_text)
    await update.message.reply_text(package_message)
    
    # عرض أزرار الكمية أولاً (مثل الستاتيك)
    if language == 'ar':
        keyboard = [
            [InlineKeyboardButton(f"🔸 بروكسي واحد ({single_price}$)", callback_data="quantity_one_socks")],
            [InlineKeyboardButton(f"🔸 بروكسيان اثنان ({double_price}$)", callback_data="quantity_two_socks")],
            [InlineKeyboardButton(f"📦 باكج 5 ({package5_price}$)", callback_data="quantity_single_socks")],
            [InlineKeyboardButton(f"📦 باكج 10 ({package10_price}$)", callback_data="quantity_package_socks")],
            [InlineKeyboardButton("🔙 رجوع", callback_data="cancel_user_proxy_request")]
        ]
        quantity_text = "اختر الكمية المطلوبة:"
    else:
        keyboard = [
            [InlineKeyboardButton(f"🔸 One Proxy ({single_price}$)", callback_data="quantity_one_socks")],
            [InlineKeyboardButton(f"🔸 Two Proxies ({double_price}$)", callback_data="quantity_two_socks")],
            [InlineKeyboardButton(f"📦 Package 5 ({package5_price}$)", callback_data="quantity_single_socks")],
            [InlineKeyboardButton(f"📦 Package 10 ({package10_price}$)", callback_data="quantity_package_socks")],
            [InlineKeyboardButton("🔙 Back", callback_data="cancel_user_proxy_request")]
        ]
        quantity_text = "Choose the required quantity:"
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(quantity_text, reply_markup=reply_markup)
    context.user_data['proxy_type'] = 'socks'
    return

async def handle_country_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالجة اختيار الدولة"""
    try:
        query = update.callback_query
        user_id = update.effective_user.id
        
        # تسجيل الإجراء
        logger.info(f"User {user_id} selected: {query.data}")
        
        try:
            await query.answer()
        except Exception as answer_error:
            logger.warning(f"Failed to answer country callback for user {user_id}: {answer_error}")
        
        language = get_user_language(user_id)
        
        # معالجة خاصة للستاتيك الأسبوعي
        if query.data.startswith("country_") and query.data.endswith("_weekly"):
            country_code = query.data.replace("country_", "").replace("_weekly", "")
            context.user_data['selected_country_code'] = country_code
            
            # تحديد اسم الدولة
            if country_code == 'US':
                country_name = 'الولايات المتحدة' if language == 'ar' else 'United States'
            else:
                country_name = country_code
                
            context.user_data['selected_country'] = country_name
            
            # أمريكا - عرض الولايات
            try:
                states = STATIC_WEEKLY_LOCATIONS[language][country_code]
                
                keyboard = []
                for state_code, state_name in states.items():
                    keyboard.append([InlineKeyboardButton(
                        f"📍 {state_name}", 
                        callback_data=f"state_{state_code}_weekly"
                    )])
                
                keyboard.append([InlineKeyboardButton(
                    "🔙 رجوع" if language == 'ar' else "🔙 Back", 
                    callback_data="cancel_user_proxy_request"
                )])
                
                reply_markup = InlineKeyboardMarkup(keyboard)
                message = f"🏛️ اختر الولاية في {country_name}:" if language == 'ar' else f"🏛️ Choose state in {country_name}:"
                await query.edit_message_text(message, reply_markup=reply_markup)
            except Exception as e:
                logger.error(f"Error displaying weekly states for {country_code}: {e}")
                await query.edit_message_text("❌ خطأ في عرض الولايات" if language == 'ar' else "❌ Error displaying states")
            return
            
        elif query.data.startswith("state_") and query.data.endswith("_weekly"):
            # معالجة اختيار الولاية للستاتيك الأسبوعي
            state_code = query.data.replace("state_", "").replace("_weekly", "")
            country_code = context.user_data.get('selected_country_code', 'US')
            
            try:
                # تحديد اسم الولاية
                states = STATIC_WEEKLY_LOCATIONS[language][country_code]
                state_name = states.get(state_code, state_code)
                
                context.user_data['selected_state'] = state_name
                context.user_data['selected_state_code'] = state_code
                
                # سؤال المستخدم عن الكمية قبل إنشاء الطلب
                await ask_static_proxy_quantity(query, context, language)
            except Exception as e:
                logger.error(f"Error handling weekly state selection: {e}")
                await query.edit_message_text("❌ خطأ في معالجة اختيار الولاية" if language == 'ar' else "❌ Error processing state selection")
            return
        
        # معالجة خاصة لاختيار أمريكا لـ Verizon
        elif query.data == "country_US_verizon":
            context.user_data['selected_country_code'] = 'US'
            context.user_data['selected_country'] = 'الولايات المتحدة' if language == 'ar' else 'United States'
            # عرض ولايات Verizon (NY, VA, WA)
            states = US_STATES_STATIC_VERIZON[language]
            keyboard = []
            for state_code, state_name in states.items():
                keyboard.append([InlineKeyboardButton(f"📍 {state_name}", callback_data=f"state_{state_code}_verizon")])
            keyboard.append([InlineKeyboardButton("🔙 رجوع" if language == 'ar' else "🔙 Back", callback_data="cancel_user_proxy_request")])
            reply_markup = InlineKeyboardMarkup(keyboard)
            state_text = "اختر الولاية:" if language == 'ar' else "Choose state:"
            await query.edit_message_text(state_text, reply_markup=reply_markup)
            logger.info(f"=== VERIZON US COUNTRY SELECTED ===")
            return
        
        # معالجة خاصة لاختيار أمريكا لـ Crocker
        elif query.data == "country_US_crocker":
            context.user_data['selected_country_code'] = 'US'
            context.user_data['selected_country'] = 'الولايات المتحدة' if language == 'ar' else 'United States'
            # عرض ولاية Crocker (Massachusetts فقط)
            states = US_STATES_STATIC_CROCKER[language]
            keyboard = []
            for state_code, state_name in states.items():
                keyboard.append([InlineKeyboardButton(f"📍 {state_name}", callback_data=f"state_{state_code}_crocker")])
            keyboard.append([InlineKeyboardButton("🔙 رجوع" if language == 'ar' else "🔙 Back", callback_data="cancel_user_proxy_request")])
            reply_markup = InlineKeyboardMarkup(keyboard)
            state_text = "اختر الولاية:" if language == 'ar' else "Choose state:"
            await query.edit_message_text(state_text, reply_markup=reply_markup)
            logger.info(f"=== CROCKER US COUNTRY SELECTED ===")
            return
        
        if query.data.startswith("country_"):
            country_code = query.data.replace("country_", "")
            # حفظ اسم الدولة الكامل مع العلم بدلاً من الرمز فقط
            proxy_type = context.user_data.get('proxy_type')
            if proxy_type == 'socks':
                country_name = SOCKS_COUNTRIES[language].get(country_code, country_code)
            else:
                country_name = STATIC_COUNTRIES[language].get(country_code, country_code)
            context.user_data['selected_country'] = country_name
            context.user_data['selected_country_code'] = country_code
            
            # فحص وجود ولايات للدولة
            # تحديد نوع البروكسي الفرعي للستاتيك
            proxy_subtype = 'residential'  # افتراضي للريزيدنتال
            if proxy_type == 'static':
                # التحقق من نوع الستاتيك المطلوب من context
                static_type = context.user_data.get('static_type', '')
                if static_type == 'isp':
                    proxy_subtype = 'isp'
                elif static_type == 'residential_verizon':
                    proxy_subtype = 'residential_verizon'
                else:
                    proxy_subtype = 'residential'  # للريزيدنتال العادي
            
            states = get_states_for_country(country_code, proxy_type, proxy_subtype)
            if states:
                # عرض الولايات
                states_dict = states.get(language, states.get('ar', {}))
                keyboard = []
                for state_code, state_name in states_dict.items():
                    keyboard.append([InlineKeyboardButton(state_name, callback_data=f"state_{state_code}")])
                
                keyboard.append([InlineKeyboardButton("🔙 رجوع", callback_data="cancel_user_proxy_request")])
                
                reply_markup = InlineKeyboardMarkup(keyboard)
                await query.edit_message_text(
                    MESSAGES[language]['select_state'],
                    reply_markup=reply_markup
                )
            else:
                # الانتقال لاختيار الكمية إذا لم تكن هناك ولايات
                context.user_data['selected_state'] = country_name
                context.user_data['selected_state_code'] = country_code
                
                # عرض رسالة اختيار الكمية
                if language == 'ar':
                    keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data="cancel_user_proxy_request")]]
                else:
                    keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="cancel_user_proxy_request")]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                # تحديد الكمية تلقائياً بناءً على نوع الطلب
                proxy_type = context.user_data.get('proxy_type')
                quantity_type = context.user_data.get('quantity', '5')  # افتراضي 5
                
                # تحويل الكمية من string إلى int
                if isinstance(quantity_type, str):
                    try:
                        context.user_data['quantity'] = int(quantity_type)
                    except (ValueError, TypeError):
                        context.user_data['quantity'] = 5  # افتراضي
                else:
                    context.user_data['quantity'] = quantity_type or 5
                
                # للبروكسي الستاتيك: الانتقال لسؤال الكمية قبل إنشاء الطلب
                if proxy_type == 'static':
                    await ask_static_proxy_quantity(query, context, language)
                else:
                    # إنشاء الطلب مباشرة للأنواع الأخرى
                    try:
                        order_id = await create_order_directly_from_callback(update, context, language)
                        
                        # إرسال رسالة تأكيد
                        if language == 'ar':
                            success_message = f"""✅ تم إرسال طلبك بنجاح!

🆔 معرف الطلب: <code>{order_id}</code>
⏰ سيتم مراجعة طلبك من قبل الإدارة وإرسال البيانات قريباً

📞 للاستفسار عن الطلب تواصل مع الدعم"""
                        else:
                            success_message = f"""✅ Your order has been sent successfully!

🆔 Order ID: <code>{order_id}</code>
⏰ Your order will be reviewed by management and data sent soon

📞 For inquiry contact support"""
                        
                        await query.edit_message_text(success_message, parse_mode='HTML')
                        return ConversationHandler.END
                        
                    except Exception as order_error:
                        logger.error(f"Error creating order from callback: {order_error}")
                        # التحقق من نوع الخطأ لعرض الرسالة المناسبة
                        error_message = str(order_error)
                        if "رصيد غير كافي" in error_message or "Insufficient balance" in error_message:
                            # عرض رسالة الرصيد غير الكافي
                            await query.edit_message_text(error_message, parse_mode='Markdown')
                        else:
                            # عرض رسالة خطأ عامة
                            await query.edit_message_text(
                                "❌ حدث خطأ في إنشاء الطلب. يرجى المحاولة مرة أخرى أو التواصل مع الدعم.",
                                parse_mode='Markdown'
                            )
                        return ConversationHandler.END
        
        elif query.data.endswith("_verizon") and query.data.startswith("state_"):
            # معالجة اختيار ولاية Verizon
            state_code = query.data.replace("state_", "").replace("_verizon", "")
            context.user_data['selected_country_code'] = 'US'
            context.user_data['selected_state_code'] = state_code
            state_name = US_STATES_STATIC_VERIZON[language].get(state_code, state_code)
            context.user_data['selected_state'] = state_name
            # الانتقال لسؤال الكمية
            await ask_static_proxy_quantity(query, context, language)
            logger.info(f"=== VERIZON STATE SELECTED: {state_code} ===")
            
        elif query.data.endswith("_crocker") and query.data.startswith("state_"):
            # معالجة اختيار ولاية Crocker
            state_code = query.data.replace("state_", "").replace("_crocker", "")
            context.user_data['selected_country_code'] = 'US'
            context.user_data['selected_state_code'] = state_code
            state_name = US_STATES_STATIC_CROCKER[language].get(state_code, state_code)
            context.user_data['selected_state'] = state_name
            # الانتقال لسؤال الكمية
            await ask_static_proxy_quantity(query, context, language)
            logger.info(f"=== CROCKER STATE SELECTED: {state_code} ===")
            
        elif query.data.startswith("state_"):
            # معالجة اختيار الولاية
            state_code = query.data.replace("state_", "")
            country_code = context.user_data.get('selected_country_code', '')
            
            # حفظ الولاية المختارة
            proxy_type = context.user_data.get('proxy_type')
            proxy_subtype = 'residential'
            if proxy_type == 'static':
                static_type = context.user_data.get('static_type', '')
                if static_type == 'isp':
                    proxy_subtype = 'isp'
            
            states = get_states_for_country(country_code, proxy_type, proxy_subtype)
            if states:
                state_name = states.get(language, states.get('ar', {})).get(state_code, state_code)
                context.user_data['selected_state'] = state_name
                context.user_data['selected_state_code'] = state_code
                
                # التأكد من حفظ اسم الدولة أيضاً (مهم للسوكس مع الولايات)
                if not context.user_data.get('selected_country'):
                    if proxy_type == 'socks':
                        country_name = SOCKS_COUNTRIES[language].get(country_code, country_code)
                    else:
                        country_name = STATIC_COUNTRIES[language].get(country_code, country_code)
                    context.user_data['selected_country'] = country_name
            
            # الانتقال لاختيار الكمية بدون طرق الدفع
            if language == 'ar':
                keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data="cancel_user_proxy_request")]]
            else:
                keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="cancel_user_proxy_request")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # تحديد الكمية تلقائياً بناءً على نوع الطلب
            quantity_type = context.user_data.get('quantity', '5')  # افتراضي 5
            
            # تحويل الكمية من string إلى int
            if isinstance(quantity_type, str):
                try:
                    context.user_data['quantity'] = int(quantity_type)
                except (ValueError, TypeError):
                    context.user_data['quantity'] = 5  # افتراضي
            else:
                context.user_data['quantity'] = quantity_type or 5
            
            # للبروكسي الستاتيك: الانتقال لسؤال الكمية قبل إنشاء الطلب
            # للسوكس: الكمية محددة بالفعل، إنشاء الطلب مباشرة
            if proxy_type == 'static':
                await ask_static_proxy_quantity(query, context, language)
            else:
                # إنشاء الطلب مباشرة للأنواع الأخرى
                try:
                    order_id = await create_order_directly_from_callback(update, context, language)
                    
                    # إرسال رسالة تأكيد
                    if language == 'ar':
                        success_message = f"""✅ تم إرسال طلبك بنجاح!

🆔 معرف الطلب: {order_id}
⏰ سيتم مراجعة طلبك من قبل الإدارة وإرسال البيانات قريباً

📞 للاستفسار عن الطلب تواصل مع الدعم"""
                    else:
                        success_message = f"""✅ Your order has been sent successfully!

🆔 Order ID: {order_id}
⏰ Your order will be reviewed by management and data sent soon

📞 For inquiry contact support"""
                    
                    await query.edit_message_text(success_message, parse_mode='Markdown')
                    return ConversationHandler.END
                    
                except Exception as order_error:
                    logger.error(f"Error creating order from callback: {order_error}")
                    # التحقق من نوع الخطأ لعرض الرسالة المناسبة
                    error_message = str(order_error)
                    if "رصيد غير كافي" in error_message or "Insufficient balance" in error_message:
                        # عرض رسالة الرصيد غير الكافي
                        await query.edit_message_text(error_message, parse_mode='Markdown')
                    else:
                        # عرض رسالة خطأ عامة
                        await query.edit_message_text(
                            "❌ حدث خطأ في إنشاء الطلب. يرجى المحاولة مرة أخرى أو التواصل مع الدعم.",
                            parse_mode='Markdown'
                        )
                    return ConversationHandler.END
        
    except Exception as e:
        logger.error(f"Error in show_payment_methods: {e}")
        
        try:
            # محاولة إرسال رسالة خطأ بسيطة
            await query.message.reply_text(
                "⚠️ حدث خطأ في عرض طرق الدفع. يرجى استخدام /start لإعادة المحاولة.",
                reply_markup=ReplyKeyboardRemove()
            )
        except Exception as recovery_error:
            logger.error(f"Failed to send error message in show_payment_methods: {recovery_error}")

async def handle_payment_method_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """معالجة اختيار طريقة الدفع"""
    try:
        query = update.callback_query
        user_id = update.effective_user.id
        
        # تسجيل الإجراء
        logger.info(f"User {user_id} selected payment method: {query.data}")
        
        try:
            await query.answer()
        except Exception as answer_error:
            logger.warning(f"Failed to answer payment callback for user {user_id}: {answer_error}")
        
        language = get_user_language(user_id)
        
        payment_method = query.data.replace("payment_", "")
        context.user_data['payment_method'] = payment_method
        
        # فحص نوع البروكسي - إذا كان سوكس، تخطى سؤال الكمية (تم تحديدها بالفعل)
        proxy_type = context.user_data.get('proxy_type')
        
        if proxy_type == 'socks':
            # للسوكس: الكمية محددة بالفعل، انتقل مباشرة لإثبات الدفع
            await query.edit_message_text(
                MESSAGES[language]['send_payment_proof']
            )
            return PAYMENT_PROOF
        else:
            # للستاتيك: اسأل عن الكمية كالمعتاد
            # إضافة زر الإلغاء
            if language == 'ar':
                keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data="cancel_payment_proof")]]
            else:
                keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="cancel_payment_proof")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # تحديد الكمية تلقائياً بناءً على نوع الطلب
            quantity_type = context.user_data.get('quantity', '5')  # افتراضي 5
            
            # تحويل الكمية من string إلى int
            if isinstance(quantity_type, str):
                try:
                    context.user_data['quantity'] = int(quantity_type)
                except (ValueError, TypeError):
                    context.user_data['quantity'] = 5  # افتراضي
            else:
                context.user_data['quantity'] = quantity_type or 5
            
            # إنشاء الطلب مباشرة
            try:
                order_id = await create_order_directly_from_callback(update, context, language)
                
                # إرسال رسالة تأكيد
                if language == 'ar':
                    success_message = f"""✅ تم إرسال طلبك بنجاح!

🆔 معرف الطلب: <code>{order_id}</code>
⏰ سيتم مراجعة طلبك من قبل الإدارة وإرسال البيانات قريباً

📞 للاستفسار عن الطلب تواصل مع الدعم"""
                else:
                    success_message = f"""✅ Your order has been sent successfully!

🆔 Order ID: <code>{order_id}</code>
⏰ Your order will be reviewed by management and data sent soon

📞 For inquiry contact support"""
                
                await query.edit_message_text(success_message, parse_mode='HTML')
                return ConversationHandler.END
                
            except Exception as order_error:
                logger.error(f"Error creating order from callback in payment method: {order_error}")
                await query.edit_message_text(
                    "❌ حدث خطأ في إنشاء الطلب. يرجى المحاولة مرة أخرى أو التواصل مع الدعم.",
                    parse_mode='Markdown'
                )
                return ConversationHandler.END
        
    except Exception as e:
        logger.error(f"Error in handle_payment_method_selection for user {user_id}: {e}")
        
        try:
            await update.callback_query.message.reply_text(
                "⚠️ حدث خطأ في معالجة طريقة الدفع. تم إعادة تعيين حالتك.\n"
                "يرجى استخدام /start لإعادة المحاولة.",
                reply_markup=ReplyKeyboardRemove()
            )
            # تنظيف البيانات المؤقتة
            context.user_data.clear()
            
        except Exception as recovery_error:
            logger.error(f"Failed to send error message in payment method selection: {recovery_error}")
        
        return ConversationHandler.END

async def ask_static_proxy_quantity(query, context: ContextTypes.DEFAULT_TYPE, language: str) -> None:
    """سؤال المستخدم عن كمية البروكسي الستاتيك (1-100)"""
    try:
        if language == 'ar':
            message = """🔢 اختر كمية البروكسي المطلوبة:

⚠️ يجب أن تكون الكمية من 1 إلى 100

📝 اكتب الرقم المطلوب:"""
            keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data="cancel_user_proxy_request")]]
        else:
            message = """🔢 Choose the required proxy quantity:

⚠️ Quantity must be between 1 and 100

📝 Enter the required number:"""
            keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="cancel_user_proxy_request")]]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # وضع علامة أننا في مرحلة انتظار الكمية
        context.user_data['waiting_for_static_quantity'] = True
        
        await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Error in ask_static_proxy_quantity: {e}")
        await query.edit_message_text(
            "❌ حدث خطأ في عرض خيارات الكمية. يرجى المحاولة مرة أخرى.",
            parse_mode='Markdown'
        )

async def handle_static_quantity_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالجة إدخال كمية البروكسي الستاتيك"""
    try:
        user_id = update.effective_user.id
        language = get_user_language(user_id)
        
        # التحقق من أننا في انتظار كمية ستاتيك
        if not context.user_data.get('waiting_for_static_quantity'):
            return
        
        quantity_text = update.message.text.strip()
        
        # التحقق من أن النص يحتوي على رقم صحيح فقط
        if not quantity_text.isdigit():
            if language == 'ar':
                await update.message.reply_text(
                    "❌ يرجى إدخال رقم صحيح فقط (من 1 إلى 100)",
                    parse_mode='Markdown'
                )
            else:
                await update.message.reply_text(
                    "❌ Please enter a valid number only (1 to 100)",
                    parse_mode='Markdown'
                )
            return
        
        quantity = int(quantity_text)
        
        # التحقق من أن العدد بين 1 و 100
        if quantity < 1 or quantity > 100:
            if language == 'ar':
                await update.message.reply_text(
                    "❌ الكمية يجب أن تكون بين 1 و 100",
                    parse_mode='Markdown'
                )
            else:
                await update.message.reply_text(
                    "❌ Quantity must be between 1 and 100",
                    parse_mode='Markdown'
                )
            return
        
        # حفظ الكمية وإزالة علامة الانتظار
        context.user_data['quantity'] = quantity
        context.user_data.pop('waiting_for_static_quantity', None)
        
        # التحقق من الرصيد قبل إنشاء الطلب
        try:
            # حساب التكلفة الإجمالية
            proxy_type = context.user_data.get('proxy_type', 'static')
            selected_country = context.user_data.get('selected_country', 'US')
            selected_state = context.user_data.get('selected_state', '')
            static_type = context.user_data.get('static_type', '')
            
            # حساب سعر الوحدة
            unit_price = get_proxy_price(proxy_type, selected_country, selected_state, static_type)
            total_cost = unit_price * quantity
            
            # الحصول على رصيد المستخدم الحالي
            user = db.get_user(user_id)
            if not user:
                raise ValueError("User not found")
            
            current_balance = float(user[6]) if user[6] else 0.0  # الرصيد في العمود السابع (points_balance)
            
            # التحقق من كفاية الرصيد
            if current_balance < total_cost:
                if language == 'ar':
                    insufficient_message = f"""❌ رصيد غير كافي

💰 التكلفة الإجمالية: `${total_cost:.2f}`
📊 الكمية: `{quantity}`
💵 سعر الوحدة: `${unit_price:.2f}`
💳 رصيدك الحالي: `${current_balance:.2f}`
📉 المطلوب إضافياً: `${(total_cost - current_balance):.2f}`

🔄 يرجى شحن رصيدك أولاً ثم إعادة المحاولة"""
                else:
                    insufficient_message = f"""❌ Insufficient balance

💰 Total cost: `${total_cost:.2f}`
📊 Quantity: `{quantity}`
💵 Unit price: `${unit_price:.2f}`
💳 Your current balance: `${current_balance:.2f}`
📉 Additional required: `${(total_cost - current_balance):.2f}`

🔄 Please recharge your balance first and try again"""
                
                await update.message.reply_text(insufficient_message, parse_mode='Markdown')
                return
            
            # إظهار تأكيد التكلفة قبل المتابعة
            if language == 'ar':
                confirmation_message = f"""✅ تم التحقق من الرصيد بنجاح

💰 التكلفة الإجمالية: `${total_cost:.2f}`
📊 الكمية: `{quantity}`
💵 سعر الوحدة: `${unit_price:.2f}`
💳 رصيدك بعد الشراء: `${(current_balance - total_cost):.2f}`

⏳ جارِ إنشاء طلبك..."""
            else:
                confirmation_message = f"""✅ Balance verified successfully

💰 Total cost: `${total_cost:.2f}`
📊 Quantity: `{quantity}`
💵 Unit price: `${unit_price:.2f}`
💳 Your balance after purchase: `${(current_balance - total_cost):.2f}`

⏳ Creating your order..."""
            
            await update.message.reply_text(confirmation_message, parse_mode='Markdown')
            
        except Exception as balance_error:
            logger.error(f"Error checking balance: {balance_error}")
            if language == 'ar':
                await update.message.reply_text(
                    """❌ خطأ في النظام المالي

🔄 فشل في التحقق من رصيدك الحالي
⚠️ قد يكون هناك مشكلة مؤقتة في قاعدة البيانات

🔧 الحلول الممكنة:
• انتظر دقيقة واحدة ثم حاول مرة أخرى
• استخدم /start لإعادة تشغيل البوت
• تواصل مع الدعم إذا استمرت المشكلة

📞 للمساعدة: @@Static_support""",
                    parse_mode='Markdown'
                )
            else:
                await update.message.reply_text(
                    """❌ Financial System Error

🔄 Failed to check your current balance
⚠️ There may be a temporary database issue

🔧 Possible solutions:
• Wait one minute and try again
• Use /start to restart the bot
• Contact support if the problem persists

📞 For help: @@Static_support""",
                    parse_mode='Markdown'
                )
            return
        
        # إنشاء الطلب الآن (بعد التحقق من الرصيد)
        try:
            order_id = await create_order_directly_from_message(update, context, language)
            
            # إرسال رسالة تأكيد
            if language == 'ar':
                success_message = f"""✅ تم إرسال طلبك بنجاح!

🆔 معرف الطلب: `{order_id}`
🔢 الكمية: {quantity}
⏰ سيتم مراجعة طلبك من قبل الإدارة وإرسال البيانات قريباً

📞 للاستفسار عن الطلب تواصل مع الدعم"""
            else:
                success_message = f"""✅ Your order has been sent successfully!

🆔 Order ID: `{order_id}`
🔢 Quantity: {quantity}
⏰ Your order will be reviewed by management and data sent soon

📞 For inquiry contact support"""
            
            await update.message.reply_text(success_message, parse_mode='Markdown')
            
        except Exception as order_error:
            logger.error(f"Error creating order after quantity input: {order_error}")
            # التحقق من نوع الخطأ لعرض الرسالة المناسبة
            error_message = str(order_error)
            if "رصيد غير كافي" in error_message or "Insufficient balance" in error_message:
                # عرض رسالة الرصيد غير الكافي
                await update.message.reply_text(error_message, parse_mode='Markdown')
            else:
                # عرض رسالة خطأ عامة
                await update.message.reply_text(
                    "❌ حدث خطأ في إنشاء الطلب. يرجى المحاولة مرة أخرى أو التواصل مع الدعم.",
                    parse_mode='Markdown'
                )
        
    except Exception as e:
        logger.error(f"Error in handle_static_quantity_input: {e}")
        language = get_user_language(update.effective_user.id)
        if language == 'ar':
            await update.message.reply_text(
                "❌ حدث خطأ في معالجة الكمية. يرجى المحاولة مرة أخرى.",
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(
                "❌ Error processing quantity. Please try again.",
                parse_mode='Markdown'
            )

async def create_order_directly_from_callback(update: Update, context: ContextTypes.DEFAULT_TYPE, language: str) -> str:
    """إنشاء الطلب مباشرة من callback query بدون طرق الدفع وإثبات الدفع"""
    try:
        user_id = update.effective_user.id if update.effective_user else update.callback_query.from_user.id
        
        # التحقق من وجود البيانات المطلوبة
        if 'proxy_type' not in context.user_data:
            raise ValueError("Proxy type not found")

        # إنشاء معرف الطلب
        try:
            order_id = generate_order_id()
        except Exception as id_error:
            logger.error(f"Error generating order ID: {id_error}")
            raise ValueError(f"Failed to generate order ID: {id_error}")
        
        # جمع بيانات الطلب
        proxy_type = context.user_data.get('proxy_type', 'socks')
        quantity = context.user_data.get('quantity', 5)
        # التأكد من أن quantity هو int (إصلاح مشكلة سوكس أمريكا)
        if isinstance(quantity, str):
            try:
                quantity = int(quantity)
            except (ValueError, TypeError):
                quantity = 5
        selected_country = context.user_data.get('selected_country', '')
        selected_state = context.user_data.get('selected_state', '')
        payment_method = context.user_data.get('payment_method', 'balance')
        
        # التحقق من وجود البيانات الأساسية
        if not selected_country:
            raise ValueError("Country not selected. Please start the order process again.")
        
        # حساب السعر الإجمالي
        try:
            # للسوكس: استخدام السعر المحفوظ مسبقاً
            if proxy_type == 'socks' and 'socks_price' in context.user_data:
                unit_price = context.user_data['socks_price']
            else:
                # للستاتيك: استخدام get_proxy_price مع static_type
                static_type = context.user_data.get('static_type', '')
                unit_price = get_proxy_price(proxy_type, selected_country, selected_state, static_type)
            
            total_price = unit_price * quantity
        except Exception as price_error:
            logger.error(f"Error calculating price: {price_error}")
            logger.error(f"Price calculation params: proxy_type={proxy_type}, country={selected_country}, state={selected_state}")
            raise ValueError(f"Failed to calculate price: {price_error}")
        
        # التحقق من كفاية الرصيد قبل إنشاء الطلب
        try:
            user_balance = db.get_user_balance(user_id)
            available_points = user_balance['total_balance']  # استخدام المجموع الكامل
            
            if available_points < total_price:
                # رصيد غير كافي - منع إنشاء الطلب
                user_language = get_user_language(user_id) if 'get_user_language' in globals() else 'ar'
                if user_language == 'ar':
                    raise ValueError(f"❌ رصيد غير كافي!\n\n💰 النقاط المطلوبة: {total_price:.2f} نقطة\n💎 رصيدك الحالي: {available_points:.2f} نقطة\n\n📞 يرجى شحن رصيدك أو التواصل مع الإدارة.")
                else:
                    raise ValueError(f"❌ Insufficient balance!\n\n💰 Points required: {total_price:.2f} points\n💎 Current balance: {available_points:.2f} points\n\n📞 Please recharge your balance or contact admin.")
                    
        except Exception as balance_error:
            if "رصيد غير كافي" in str(balance_error) or "Insufficient balance" in str(balance_error):
                # إعادة رمي خطأ الرصيد غير الكافي
                raise balance_error
            else:
                logger.error(f"Error checking balance: {balance_error}")
                raise ValueError(f"خطأ في التحقق من الرصيد: {balance_error}")
        
        # إدخال الطلب في قاعدة البيانات
        try:
            db.execute_query(
                """
                INSERT INTO orders (
                    id, user_id, proxy_type, quantity, country, state, 
                    payment_method, payment_amount, status, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (order_id, user_id, proxy_type, quantity, selected_country, 
                 selected_state, payment_method, total_price, 'pending', datetime.now().isoformat())
            )
            
            logger.info(f"Order created successfully from callback: {order_id} for user {user_id}")
            
            # إرسال إشعار للأدمن باستخدام send_admin_notification_with_details
            try:
                user_language = get_user_language(user_id)
                static_type = context.user_data.get('static_type', '')
                
                await send_admin_notification_with_details(
                    context, order_id, user_id, proxy_type, selected_country,
                    selected_state, total_price, user_language, quantity, static_type
                )
                
                logger.info(f"Admin notification sent for order: {order_id}")
                    
            except Exception as e:
                # تسجيل الخطأ فقط دون رفع Exception - الطلب تم إنشاؤه بنجاح
                logger.error(f"Error sending admin notification for order {order_id}: {e}")
                logger.error(f"Order data: proxy_type={proxy_type}, country={selected_country}, state={selected_state}")
            
            return order_id
            
        except Exception as db_error:
            logger.error(f"Database error creating order from callback: {db_error}")
            raise
            
    except Exception as e:
        # التحقق إذا كان الخطأ بسبب الرصيد غير الكافي - رفع Exception فقط في هذه الحالة
        if "رصيد غير كافي" in str(e) or "Insufficient balance" in str(e):
            raise
        # تسجيل الأخطاء الأخرى دون رفع Exception إذا كان الطلب تم إنشاؤه
        logger.error(f"Error in create_order_directly_from_callback: {e}")
        # إذا كان هناك order_id، الطلب تم إنشاؤه بنجاح
        if 'order_id' in locals():
            return order_id
        raise

async def create_order_directly_from_message(update: Update, context: ContextTypes.DEFAULT_TYPE, language: str) -> str:
    """إنشاء الطلب مباشرة من رسالة نصية بدون طرق الدفع وإثبات الدفع"""
    try:
        user_id = update.effective_user.id
        
        # التحقق من وجود البيانات المطلوبة
        if 'proxy_type' not in context.user_data:
            raise ValueError("Proxy type not found")

        # إنشاء معرف الطلب
        try:
            order_id = generate_order_id()
        except Exception as id_error:
            logger.error(f"Error generating order ID: {id_error}")
            raise ValueError(f"Failed to generate order ID: {id_error}")
        context.user_data['current_order_id'] = order_id
        
        # جمع بيانات الطلب
        proxy_type = context.user_data.get('proxy_type')
        country = context.user_data.get('selected_country', 'manual')
        state = context.user_data.get('selected_state', 'manual')
        quantity = context.user_data.get('quantity', '1')
        
        # حساب سعر البروكسي
        # للسوكس: استخدام السعر المحفوظ مسبقاً
        if proxy_type == 'socks' and 'socks_price' in context.user_data:
            unit_price = context.user_data['socks_price']
        else:
            # للستاتيك: استخدام get_proxy_price مع static_type
            static_type = context.user_data.get('static_type', '')
            unit_price = get_proxy_price(proxy_type, country, state, static_type)
        
        # تحويل الكمية إلى رقم صحيح
        try:
            quantity_int = int(quantity)
        except (ValueError, TypeError):
            quantity_int = 1
        
        # حساب التكلفة الإجمالية
        total_cost = unit_price * quantity_int
        
        # التحقق من الرصيد قبل إنشاء الطلب
        user = db.get_user(user_id)
        if not user:
            raise ValueError("User not found")
        
        current_balance = float(user[6]) if user[6] else 0.0
        
        # التحقق من كفاية الرصيد
        if current_balance < total_cost:
            if language == 'ar':
                insufficient_message = f"""❌ رصيد غير كافي

💰 التكلفة الإجمالية: ${total_cost:.2f}
📊 الكمية: {quantity_int}
💵 سعر الوحدة: ${unit_price:.2f}
💳 رصيدك الحالي: ${current_balance:.2f}
📉 المطلوب إضافياً: ${(total_cost - current_balance):.2f}

🔄 يرجى شحن رصيدك أولاً ثم إعادة المحاولة"""
            else:
                insufficient_message = f"""❌ Insufficient balance

💰 Total cost: ${total_cost:.2f}
📊 Quantity: {quantity_int}
💵 Unit price: ${unit_price:.2f}
💳 Your current balance: ${current_balance:.2f}
📉 Additional required: ${(total_cost - current_balance):.2f}

🔄 Please recharge your balance first and try again"""
            
            raise ValueError(insufficient_message)
        
        # استخدام total_cost بدلاً من payment_amount
        payment_amount = total_cost
        
        # إنشاء الطلب في قاعدة البيانات بدون payment_method (سيتم استخدام 'points' كقيمة افتراضية)
        # التحقق من وجود البيانات الكاملة
        if not all([order_id, user_id, proxy_type, country, state]):
            raise ValueError("Missing required order data")
        
        # استخدام create_order مع 'points' كطريقة الدفع الافتراضية
        db.create_order(order_id, user_id, proxy_type, country, state, 'points', payment_amount, str(quantity))
        
        # تحديث static_type إذا كان متوفراً
        if static_type:
            db.execute_query(
                "UPDATE orders SET static_type = ? WHERE id = ?",
                (static_type, order_id)
            )
        
        logger.info(f"Order created successfully: {order_id} for user {user_id}")

        # إرسال إشعار للأدمن
        try:
            global ACTIVE_ADMINS
            if ACTIVE_ADMINS:
                admin_message = create_admin_notification_message(order_id, user_id, proxy_type, country, state, payment_amount, language, quantity, static_type)
                
                keyboard = [[InlineKeyboardButton("⚡ معالجة الطلب", callback_data=f"process_{order_id}")]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                # إرسال الإشعار لجميع الآدمن النشطين
                for admin_id in ACTIVE_ADMINS:
                    try:
                        await context.bot.send_message(
                            admin_id,
                            admin_message,
                            reply_markup=reply_markup,
                            parse_mode='Markdown'
                        )
                    except Exception as admin_error:
                        logger.error(f"Error sending notification to admin {admin_id}: {admin_error}")
                
                logger.info(f"Admin notification sent for order: {order_id}")
                
        except Exception as e:
            logger.error(f"Error sending admin notification for order {order_id}: {e}")
        
        # تسجيل العملية
        try:
            db.log_action(user_id, "order_created_directly", order_id)
        except Exception as e:
            logger.error(f"Error logging action for order {order_id}: {e}")

        # تنظيف البيانات المؤقتة وإنهاء المحادثة مع الحفاظ على حالة الأدمن
        clean_user_data_preserve_admin(context)
        
        return order_id
        
    except Exception as e:
        logger.error(f"Error in create_order_directly_from_message for user {user_id}: {e}")
        raise e

async def create_order_directly(query, context: ContextTypes.DEFAULT_TYPE, language: str) -> None:
    """إنشاء الطلب مباشرة بدون طرق الدفع وإثبات الدفع"""
    try:
        user_id = query.from_user.id
        
        # التحقق من وجود البيانات المطلوبة
        if 'proxy_type' not in context.user_data:
            await query.edit_message_text(
                "❌ خطأ: لم يتم العثور على نوع البروكسي. يرجى البدء من جديد بالضغط على /start" if language == 'ar' else 
                "❌ Error: Proxy type not found. Please start over with /start"
            )
            return

        # إنشاء معرف الطلب
        try:
            order_id = generate_order_id()
        except Exception as id_error:
            logger.error(f"Error generating order ID: {id_error}")
            raise ValueError(f"Failed to generate order ID: {id_error}")
        context.user_data['current_order_id'] = order_id
        
        # جمع بيانات الطلب
        proxy_type = context.user_data.get('proxy_type')
        country = context.user_data.get('selected_country', 'manual')
        state = context.user_data.get('selected_state', 'manual')
        quantity = context.user_data.get('quantity', '1')
        
        # حساب سعر البروكسي
        # للسوكس: استخدام السعر المحفوظ مسبقاً
        if proxy_type == 'socks' and 'socks_price' in context.user_data:
            unit_price = context.user_data['socks_price']
        else:
            # للستاتيك: استخدام get_proxy_price مع static_type
            static_type = context.user_data.get('static_type', '')
            unit_price = get_proxy_price(proxy_type, country, state, static_type)
        
        # تحويل الكمية إلى رقم صحيح
        try:
            quantity_int = int(quantity)
        except (ValueError, TypeError):
            quantity_int = 1
        
        # حساب التكلفة الإجمالية
        total_cost = unit_price * quantity_int
        
        # التحقق من الرصيد قبل إنشاء الطلب
        try:
            user = db.get_user(user_id)
            if not user:
                await query.edit_message_text(
                    "❌ خطأ: لم يتم العثور على المستخدم" if language == 'ar' else 
                    "❌ Error: User not found"
                )
                return
            
            current_balance = float(user[6]) if user[6] else 0.0
            
            # التحقق من كفاية الرصيد
            if current_balance < total_cost:
                if language == 'ar':
                    insufficient_message = f"""❌ رصيد غير كافي

💰 التكلفة الإجمالية: `${total_cost:.2f}`
📊 الكمية: `{quantity_int}`
💵 سعر الوحدة: `${unit_price:.2f}`
💳 رصيدك الحالي: `${current_balance:.2f}`
📉 المطلوب إضافياً: `${(total_cost - current_balance):.2f}`

🔄 يرجى شحن رصيدك أولاً ثم إعادة المحاولة"""
                else:
                    insufficient_message = f"""❌ Insufficient balance

💰 Total cost: `${total_cost:.2f}`
📊 Quantity: `{quantity_int}`
💵 Unit price: `${unit_price:.2f}`
💳 Your current balance: `${current_balance:.2f}`
📉 Additional required: `${(total_cost - current_balance):.2f}`

🔄 Please recharge your balance first and try again"""
                
                await query.edit_message_text(insufficient_message, parse_mode='Markdown')
                return
            
        except Exception as balance_error:
            logger.error(f"Error checking balance in create_order_directly: {balance_error}")
            if language == 'ar':
                error_message = """❌ خطأ في النظام المالي

🔄 فشل في التحقق من رصيدك قبل إنشاء الطلب
⚠️ قد يكون هناك مشكلة مؤقتة في قاعدة البيانات

🔧 الحلول الممكنة:
• انتظر دقيقة واحدة ثم حاول مرة أخرى
• استخدم /start لإعادة تشغيل البوت
• تواصل مع الدعم إذا استمرت المشكلة

📞 للمساعدة: @@Static_support"""
            else:
                error_message = """❌ Financial System Error

🔄 Failed to check your balance before creating order
⚠️ There may be a temporary database issue

🔧 Possible solutions:
• Wait one minute and try again
• Use /start to restart the bot
• Contact support if the problem persists

📞 For help: @@Static_support"""
            
            await query.edit_message_text(error_message, parse_mode='Markdown')
            return
        
        # استخدام total_cost بدلاً من payment_amount
        payment_amount = total_cost
        
        # إنشاء الطلب في قاعدة البيانات بدون payment_method (سيتم استخدام 'points' كقيمة افتراضية)
        try:
            # التحقق من وجود البيانات الكاملة
            if not all([order_id, user_id, proxy_type, country, state]):
                raise ValueError("Missing required order data")
            
            # استخدام create_order مع 'points' كطريقة الدفع الافتراضية
            db.create_order(order_id, user_id, proxy_type, country, state, 'points', payment_amount, str(quantity))
            
            # تحديث static_type إذا كان متوفراً
            if static_type:
                db.execute_query(
                    "UPDATE orders SET static_type = ? WHERE id = ?",
                    (static_type, order_id)
                )
            
            logger.info(f"Order created successfully: {order_id} for user {user_id}")
            
        except Exception as e:
            logger.error(f"Error creating order: {e}")
            # إضافة معلومات debug أكثر
            logger.error(f"Order data: proxy_type={proxy_type}, country={country}, state={state}, quantity={quantity}")
            await query.edit_message_text(
                "❌ حدث خطأ في إنشاء الطلب. يرجى المحاولة مرة أخرى." if language == 'ar' else 
                "❌ Error creating order. Please try again."
            )
            return

        # إرسال إشعار للأدمن
        try:
            global ACTIVE_ADMINS
            if ACTIVE_ADMINS:
                admin_message = create_admin_notification_message(order_id, user_id, proxy_type, country, state, payment_amount, language, quantity, static_type)
                
                keyboard = [[InlineKeyboardButton("⚡ معالجة الطلب", callback_data=f"process_{order_id}")]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                # إرسال الإشعار لجميع الآدمن النشطين
                for admin_id in ACTIVE_ADMINS:
                    try:
                        await context.bot.send_message(
                            admin_id,
                            admin_message,
                            reply_markup=reply_markup,
                            parse_mode='Markdown'
                        )
                    except Exception as admin_error:
                        logger.error(f"Error sending notification to admin {admin_id}: {admin_error}")
                
                logger.info(f"Admin notification sent for order: {order_id}")
                
        except Exception as e:
            logger.error(f"Error sending admin notification for order {order_id}: {e}")

        # إرسال رسالة تأكيد للمستخدم
        if language == 'ar':
            user_message = f"""✅ تم إنشاء طلبك بنجاح!

🆔 معرف الطلب: `{order_id}`
📦 نوع البروكسي: {proxy_type}
🌍 الدولة: {country}
🏛️ الولاية: {state}
💰 السعر: {payment_amount:.2f} دولار
📊 الكمية: {quantity}

⏳ سيتم مراجعة طلبك من قبل الإدارة وستحصل على البروكسي قريباً.
💎 سيتم خصم النقاط من رصيدك عند قبول الطلب."""
        else:
            user_message = f"""✅ Your order has been created successfully!

🆔 Order ID: `{order_id}`
📦 Proxy Type: {proxy_type}
🌍 Country: {country}
🏛️ State: {state}
💰 Price: {payment_amount:.2f} USD
📊 Quantity: {quantity}

⏳ Your order will be reviewed by admin and you'll receive your proxy soon.
💎 Points will be deducted from your balance when order is approved."""

        await query.edit_message_text(user_message, parse_mode='Markdown')
        
        # تسجيل العملية
        try:
            db.log_action(user_id, "order_created_directly", order_id)
        except Exception as e:
            logger.error(f"Error logging action for order {order_id}: {e}")

        # تنظيف البيانات المؤقتة وإنهاء المحادثة مع الحفاظ على حالة الأدمن
        clean_user_data_preserve_admin(context)
        
    except Exception as e:
        logger.error(f"Error in create_order_directly for user {user_id}: {e}")
        try:
            await query.edit_message_text(
                "❌ حدث خطأ أثناء إنشاء الطلب. يرجى المحاولة مرة أخرى أو التواصل مع الدعم." if language == 'ar' else
                "❌ Error occurred while creating order. Please try again or contact support."
            )
        except:
            pass

async def handle_payment_proof(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """معالجة إثبات الدفع"""
    user_id = update.effective_user.id
    language = get_user_language(user_id)
    
    try:
        # التحقق من وجود البيانات المطلوبة
        if 'proxy_type' not in context.user_data:
            await update.message.reply_text(
                "❌ خطأ: لم يتم العثور على نوع البروكسي. يرجى البدء من جديد بالضغط على /start",
                parse_mode='Markdown'
            )
            clean_user_data_preserve_admin(context)
            return ConversationHandler.END
        
        # إنشاء معرف الطلب الآن فقط عند إرسال إثبات الدفع
        order_id = generate_order_id()
        context.user_data['current_order_id'] = order_id
        
        # إنشاء الطلب في قاعدة البيانات
        proxy_type = context.user_data.get('proxy_type')
        country = context.user_data.get('selected_country', 'manual')
        state = context.user_data.get('selected_state', 'manual')
        payment_method = context.user_data.get('payment_method', 'unknown')
        
        # حساب سعر البروكسي
        static_type = context.user_data.get('static_type', '')
        payment_amount = get_proxy_price(proxy_type, country, state, static_type)
        
        # التحقق من أن الرسالة تحتوي على صورة فقط أولاً
        if not update.message.photo:
            # رفض أي نوع آخر غير الصورة
            await update.message.reply_text(
                "❌ يُسمح بإرسال الصور فقط كإثبات للدفع!\n\n📸 يرجى إرسال صورة واضحة لإثبات الدفع\n\n⏳ البوت ينتظر صورة إثبات الدفع أو يمكنك الإلغاء",
                parse_mode='Markdown'
            )
            return PAYMENT_PROOF  # البقاء في نفس الحالة

        # معالجة إثبات الدفع (صورة فقط)
        file_id = update.message.photo[-1].file_id
        payment_proof = f"photo:{file_id}"
        
        print(f"📸 تم استلام إثبات دفع (صورة) للطلب: {order_id}")
        
        # إنشاء الطلب في قاعدة البيانات فقط بعد التحقق من الصورة
        print(f"📝 إنشاء طلب جديد: {order_id}")
        db.create_order(order_id, user_id, proxy_type, country, state, payment_method, payment_amount, context.user_data.get("quantity", "5"))
        
        # حفظ نوع البروكسي المفصل للطلب
        if static_type:
            try:
                db.execute_query("UPDATE orders SET static_type = ? WHERE id = ?", (static_type, order_id))
                print(f"💾 تم حفظ نوع البروكسي المفصل: {static_type}")
            except Exception as e:
                print(f"خطأ في حفظ نوع البروكسي: {e}")
        
        # إرسال نسخة للمستخدم
        await update.message.reply_photo(
            photo=file_id,
            caption=f"📸 إثبات دفع للطلب بمعرف: `{order_id}`\n\n✅ تم حفظ إثبات الدفع بنجاح",
            parse_mode='Markdown'
        )
        
        # حفظ إثبات الدفع في قاعدة البيانات
        if payment_proof:
            db.update_order_payment_proof(order_id, payment_proof)
            print(f"💾 تم حفظ إثبات الدفع في قاعدة البيانات للطلب: {order_id}")
        
        # إرسال نسخة من الطلب للمستخدم
        try:
            await send_order_copy_to_user(update, context, order_id)
            print(f"📋 تم إرسال نسخة الطلب للمستخدم: {order_id}")
        except Exception as e:
            print(f"⚠️ خطأ في إرسال نسخة الطلب للمستخدم {order_id}: {e}")
        
        # إرسال إشعار للأدمن مع زر المعالجة
        try:
            print(f"🔔 محاولة إرسال إشعار للأدمن للطلب: {order_id}")
            print(f"   نوع إثبات الدفع: {'صورة' if payment_proof and payment_proof.startswith('photo:') else 'نص' if payment_proof and payment_proof.startswith('text:') else 'غير معروف'}")
            await send_admin_notification(context, order_id, payment_proof)
            print(f"✅ تم إرسال إشعار الأدمن بنجاح للطلب: {order_id}")
        except Exception as e:
            print(f"❌ خطأ في إرسال إشعار الأدمن للطلب {order_id}: {e}")
            # محاولة تسجيل الخطأ
            try:
                db.log_action(user_id, "admin_notification_failed", f"Order: {order_id}, Error: {str(e)}")
            except:
                pass
        
        # إرسال رسالة تأكيد للمستخدم
        try:
            await update.message.reply_text(MESSAGES[language]['order_received'], parse_mode='Markdown')
            print(f"✅ تم إرسال رسالة التأكيد للمستخدم للطلب: {order_id}")
        except Exception as e:
            print(f"⚠️ خطأ في إرسال رسالة التأكيد للطلب {order_id}: {e}")
        
        # تسجيل العملية
        try:
            db.log_action(user_id, "payment_proof_submitted", order_id)
            print(f"📊 تم تسجيل العملية في قاعدة البيانات للطلب: {order_id}")
        except Exception as e:
            print(f"⚠️ خطأ في تسجيل العملية للطلب {order_id}: {e}")
        
        # تنظيف البيانات المؤقتة وإنهاء المحادثة مع الحفاظ على حالة الأدمن
        clean_user_data_preserve_admin(context)
        print(f"🧹 تم تنظيف البيانات المؤقتة وإنهاء معالجة الطلب: {order_id}")
        
        return ConversationHandler.END
        
    except Exception as e:
        print(f"❌ خطأ عام في معالجة إثبات الدفع للمستخدم {user_id}: {e}")
        try:
            await update.message.reply_text(
                "❌ حدث خطأ أثناء معالجة إثبات الدفع. يرجى المحاولة مرة أخرى أو التواصل مع الدعم.",
                parse_mode='Markdown'
            )
        except:
            pass
        
        # تنظيف البيانات في حالة الخطأ مع الحفاظ على حالة الأدمن
        clean_user_data_preserve_admin(context)
        return ConversationHandler.END

async def send_withdrawal_notification(context: ContextTypes.DEFAULT_TYPE, withdrawal_id: str, user: tuple) -> None:
    """إرسال إشعار طلب سحب للأدمن"""
    message = f"""💸 طلب سحب رصيد جديد

👤 الاسم: {user[2]} {user[3]}
📱 اسم المستخدم: @{user[1] or 'غير محدد'}
🆔 معرف المستخدم: `{user[0]}`

━━━━━━━━━━━━━━━
💰 المبلغ المطلوب: `{user[5]:.2f}$`
📊 نوع الطلب: سحب رصيد الإحالات

━━━━━━━━━━━━━━━
🔗 معرف الطلب: `{withdrawal_id}`
📅 تاريخ الطلب: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""

    # زر معالجة طلب السحب
    keyboard = [[InlineKeyboardButton("💸 معالجة طلب السحب", callback_data=f"process_{withdrawal_id}")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if ADMIN_CHAT_ID:
        try:
            await context.bot.send_message(
                ADMIN_CHAT_ID, 
                message, 
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        except Exception as e:
            print(f"خطأ في إرسال إشعار طلب السحب: {e}")
    
    # حفظ الإشعار في قاعدة البيانات
    db.log_action(user[0], "withdrawal_notification", f"New withdrawal: {withdrawal_id}")

async def check_and_add_referral_bonus(context: ContextTypes.DEFAULT_TYPE, user_id: int, order_id: str) -> None:
    """التحقق من إضافة رصيد الإحالة عند كل عملية شراء ناجحة للمُحال"""
    try:
        # التحقق من وجود إحالة لهذا المستخدم
        referral_query = "SELECT referrer_id FROM referrals WHERE referred_id = ?"
        referral_result = db.execute_query(referral_query, (user_id,))
        
        if referral_result:
            referrer_id = referral_result[0][0]
            
            # الحصول على مبلغ الطلب
            order_query = "SELECT payment_amount FROM orders WHERE id = ?"
            order_result = db.execute_query(order_query, (order_id,))
            payment_amount = order_result[0][0] if order_result and order_result[0][0] else 0.0
            
            # حساب قيمة الإحالة بناءً على نسبة مئوية من قيمة الطلب
            referral_bonus = get_referral_amount(payment_amount)
            db.execute_query(
                "UPDATE users SET referral_balance = referral_balance + ? WHERE user_id = ?",
                (referral_bonus, referrer_id)
            )
            
            # الحصول على بيانات المحيل والمُحال
            referrer = db.get_user(referrer_id)
            referred_user = db.get_user(user_id)
            
            if referrer and referred_user and ADMIN_CHAT_ID:
                # إشعار الأدمن بإضافة رصيد الإحالة
                admin_message = f"""💰 تم إضافة رصيد إحالة!

🎉 **عملية شراء ناجحة من المُحال**

👤 **المُحال:**
📝 الاسم: {referred_user[2]} {referred_user[3] or ''}
📱 اسم المستخدم: @{referred_user[1] or 'غير محدد'}
🆔 المعرف: `{user_id}`

━━━━━━━━━━━━━━━
👥 **المحيل:**
📝 الاسم: {referrer[2]} {referrer[3] or ''}
📱 اسم المستخدم: @{referrer[1] or 'غير محدد'}
🆔 المعرف: `{referrer_id}`

━━━━━━━━━━━━━━━
💵 **تم إضافة `{referral_bonus}$` لرصيد المحيل**
🔗 معرف الطلب: `{order_id}`
📅 التاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""

                try:
                    await context.bot.send_message(
                        ADMIN_CHAT_ID,
                        admin_message,
                        parse_mode='Markdown'
                    )
                except Exception as e:
                    print(f"خطأ في إرسال إشعار رصيد الإحالة للأدمن: {e}")
            
            # إشعار المحيل بإضافة الرصيد
            try:
                referrer_language = get_user_language(referrer_id)
                if referrer_language == 'ar':
                    referrer_message = f"""🎉 تهانينا! تم إضافة رصيد الإحالة!

💰 تم إضافة `{referral_bonus}$` إلى رصيدك
🛍️ السبب: عملية شراء ناجحة للعضو المُحال

💵 يمكنك سحب رصيدك عند وصوله إلى `1.0$`"""
                else:
                    referrer_message = f"""🎉 Congratulations! Referral bonus added!

💰 `{referral_bonus}$` added to your balance
🛍️ Reason: Successful purchase by referred member

💵 You can withdraw when balance reaches `1.0$`"""
                
                await context.bot.send_message(
                    referrer_id,
                    referrer_message,
                    parse_mode='Markdown'
                )
            except Exception as e:
                print(f"خطأ في إرسال إشعار رصيد الإحالة للمحيل: {e}")
            
            # تسجيل العملية
            db.log_action(referrer_id, "referral_bonus_added", f"Bonus: {referral_bonus}$ for order: {order_id}")
                
    except Exception as e:
        print(f"خطأ في معالجة رصيد الإحالة: {e}")

async def broadcast_referral_update(context: ContextTypes.DEFAULT_TYPE, new_percentage: float) -> None:
    """إرسال إشعار جماعي للمستخدمين بتحديث نسبة الإحالة المئوية"""
    try:
        # الحصول على جميع المستخدمين من قاعدة البيانات
        all_users_query = "SELECT user_id, language FROM users"
        users = db.execute_query(all_users_query)
        
        sent_count = 0
        failed_count = 0
        
        for user in users:
            user_id, language = user
            language = language or 'ar'  # افتراضي للعربية
            
            try:
                # تحديد الرسالة حسب اللغة
                if language == 'ar':
                    message = f"""📢 إشعار هام - تحديث نسبة الإحالة

💰 تم تحديث نسبة الإحالة إلى: {new_percentage}%

🎉 شارك رابط الإحالة الخاص بك واحصل على {new_percentage}% من كل عملية شراء!

👥 يمكنك مراجعة رصيدك من قسم "إحالاتي"

━━━━━━━━━━━━━━━
🔗 رابط الإحالة الخاص بك:
`https://t.me/{(await context.bot.get_me()).username}?start={user_id}`"""
                else:
                    message = f"""📢 Important Notice - Referral Percentage Update

💰 Referral percentage updated to: {new_percentage}%

🎉 Share your referral link and earn {new_percentage}% from every purchase!

👥 You can check your balance in "My Referrals" section

━━━━━━━━━━━━━━━
🔗 Your referral link:
`https://t.me/{(await context.bot.get_me()).username}?start={user_id}`"""
                
                await context.bot.send_message(
                    user_id,
                    message,
                    parse_mode='Markdown'
                )
                sent_count += 1
                
                # توقف قصير لتجنب حدود التيليجرام
                await asyncio.sleep(0.05)  # 50ms delay
                
            except Exception as e:
                failed_count += 1
                print(f"فشل إرسال إشعار تحديث الإحالة للمستخدم {user_id}: {e}")
        
        # إرسال تقرير للأدمن
        if ADMIN_CHAT_ID:
            admin_report = f"""📊 تقرير إشعار تحديث الإحالة

✅ تم الإرسال بنجاح: {sent_count} مستخدم
❌ فشل الإرسال: {failed_count} مستخدم
💰 النسبة الجديدة: {new_percentage}%
📅 وقت التحديث: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""
            
            try:
                await context.bot.send_message(
                    ADMIN_CHAT_ID,
                    admin_report,
                    parse_mode='Markdown'
                )
            except Exception as e:
                print(f"فشل إرسال تقرير الإشعار للأدمن: {e}")
        
        # تسجيل العملية في قاعدة البيانات
        db.log_action(ADMIN_CHAT_ID, "referral_update_broadcast", f"Percentage: {new_percentage}%, Sent: {sent_count}, Failed: {failed_count}")
        
    except Exception as e:
        print(f"خطأ في إرسال إشعار تحديث الإحالة: {e}")

async def broadcast_price_update(context: ContextTypes.DEFAULT_TYPE, price_type: str, prices: dict) -> None:
    """إرسال إشعار جماعي للمستخدمين بتحديث الأسعار"""
    try:
        # الحصول على جميع المستخدمين من قاعدة البيانات
        all_users_query = "SELECT user_id, language FROM users"
        users = db.execute_query(all_users_query)
        
        sent_count = 0
        failed_count = 0
        
        for user in users:
            user_id, language = user
            language = language or 'ar'  # افتراضي للعربية
            
            try:
                # تحديد الرسالة حسب اللغة ونوع السعر
                if price_type == "static":
                    if language == 'ar':
                        prices_text = f"""
- Static ISP Risk0: `{prices.get('ISP', '3')}$`
- Static Residential Crocker: `{prices.get('Crocker', '4')}$`
- Static Residential: `{prices.get('ATT', '6')}$`"""
                        message = f"""📢 إشعار هام - تحديث أسعار البروكسي الستاتيك

💰 تم تحديث أسعار البروكسي الستاتيك:{prices_text}

🔄 الأسعار الجديدة سارية المفعول من الآن

🛒 يمكنك طلب بروكسي ستاتيك بالأسعار الجديدة"""
                    else:
                        prices_text = f"""
- Static ISP Risk0: `{prices.get('ISP', '3')}$`
- Static Residential Crocker: `{prices.get('Crocker', '4')}$`
- Static Residential: `{prices.get('ATT', '6')}$`"""
                        message = f"""📢 Important Notice - Static Proxy Prices Update

💰 Static proxy prices have been updated:{prices_text}

🔄 New prices are effective immediately

🛒 You can order static proxy with new prices"""
                        
                elif price_type == "static_individual":
                    type_name = prices.get('type_name', 'Static')
                    price_value = ""
                    for key, value in prices.items():
                        if key != 'type_name':
                            price_value = value
                            break
                    
                    if language == 'ar':
                        message = f"""📢 إشعار هام - تحديث سعر البروكسي الستاتيك

💰 تم تحديث سعر {type_name}: `{price_value}$`

🔄 السعر الجديد ساري المفعول من الآن

🛒 يمكنك طلب بروكسي ستاتيك بالسعر الجديد"""
                    else:
                        message = f"""📢 Important Notice - Static Proxy Price Update

💰 {type_name} price has been updated: `{price_value}$`

🔄 New price is effective immediately

🛒 You can order static proxy with new price"""
                
                elif price_type == "socks":
                    if language == 'ar':
                        prices_text = f"""
- باكج 5 بروكسيات مؤقتة: `{prices.get('5proxy', '0.4')}$`
- باكج 10 بروكسيات مؤقتة: `{prices.get('10proxy', '0.7')}$`"""
                        message = f"""📢 إشعار هام - تحديث أسعار بروكسي السوكس

💰 تم تحديث أسعار بروكسي السوكس:{prices_text}

🔄 الأسعار الجديدة سارية المفعول من الآن

🛒 يمكنك طلب بروكسي سوكس بالأسعار الجديدة"""
                    else:
                        prices_text = f"""
- 5 Temporary Proxies Package: `{prices.get('5proxy', '0.4')}$`
- 10 Temporary Proxies Package: `{prices.get('10proxy', '0.7')}$`"""
                        message = f"""📢 Important Notice - Socks Proxy Prices Update

💰 Socks proxy prices have been updated:{prices_text}

🔄 New prices are effective immediately

🛒 You can order socks proxy with new prices"""
                
                elif price_type == "socks_individual":
                    type_name = prices.get('type_name', 'Socks')
                    price_value = ""
                    for key, value in prices.items():
                        if key != 'type_name':
                            price_value = value
                            break
                    
                    if language == 'ar':
                        message = f"""📢 إشعار هام - تحديث سعر بروكسي السوكس

💰 تم تحديث سعر {type_name}: `{price_value}$`

🔄 السعر الجديد ساري المفعول من الآن

🛒 يمكنك طلب بروكسي سوكس بالسعر الجديد"""
                    else:
                        message = f"""📢 Important Notice - Socks Proxy Price Update

💰 {type_name} price has been updated: `{price_value}$`

🔄 New price is effective immediately

🛒 You can order socks proxy with new price"""
                
                await context.bot.send_message(
                    user_id,
                    message,
                    parse_mode='Markdown'
                )
                sent_count += 1
                
                # توقف قصير لتجنب حدود التيليجرام
                await asyncio.sleep(0.05)  # 50ms delay
                
            except Exception as e:
                failed_count += 1
                print(f"فشل إرسال إشعار تحديث الأسعار للمستخدم {user_id}: {e}")
        
        # إرسال تقرير للأدمن
        if ADMIN_CHAT_ID:
            admin_report = f"""📊 تقرير إشعار تحديث الأسعار

📦 نوع الأسعار: {price_type}
✅ تم الإرسال بنجاح: {sent_count} مستخدم
❌ فشل الإرسال: {failed_count} مستخدم
📅 وقت التحديث: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""
            
            try:
                await context.bot.send_message(
                    ADMIN_CHAT_ID,
                    admin_report,
                    parse_mode='Markdown'
                )
            except Exception as e:
                print(f"فشل إرسال تقرير الإشعار للأدمن: {e}")
        
        # تسجيل العملية في قاعدة البيانات
        db.log_action(ADMIN_CHAT_ID, f"{price_type}_price_update_broadcast", f"Sent: {sent_count}, Failed: {failed_count}")
        
    except Exception as e:
        print(f"خطأ في إرسال إشعار تحديث الأسعار: {e}")

async def send_referral_notification(context: ContextTypes.DEFAULT_TYPE, referrer_id: int, new_user) -> None:
    """إرسال إشعار للأدمن بانضمام عضو جديد عبر الإحالة"""
    # الحصول على بيانات المحيل
    referrer = db.get_user(referrer_id)
    
    if referrer:
        message = f"""👥 عضو جديد عبر الإحالة

🆕 العضو الجديد:
👤 الاسم: {new_user.first_name} {new_user.last_name or ''}
📱 اسم المستخدم: @{new_user.username or 'غير محدد'}
🆔 معرف المستخدم: `{new_user.id}`

━━━━━━━━━━━━━━━
👥 تم إحالته بواسطة:
👤 الاسم: {referrer[2]} {referrer[3]}
📱 اسم المستخدم: @{referrer[1] or 'غير محدد'}
🆔 معرف المحيل: `{referrer[0]}`

━━━━━━━━━━━━━━━
💰 سيتم إضافة {get_referral_percentage()}% من قيمة كل عملية شراء لرصيد المحيل
📅 تاريخ الانضمام: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""

        if ADMIN_CHAT_ID:
            try:
                await context.bot.send_message(
                    ADMIN_CHAT_ID, 
                    message,
                    parse_mode='Markdown'
                )
            except Exception as e:
                print(f"خطأ في إرسال إشعار الإحالة: {e}")
        
        # حفظ الإشعار في قاعدة البيانات
        db.log_action(new_user.id, "referral_notification", f"Referred by: {referrer_id}")

async def send_order_copy_to_user(update: Update, context: ContextTypes.DEFAULT_TYPE, order_id: str) -> None:
    """إرسال نسخة من الطلب للمستخدم"""
    user_id = update.effective_user.id
    language = get_user_language(user_id)
    
    # الحصول على تفاصيل الطلب
    query = """
        SELECT o.*, u.first_name, u.last_name, u.username 
        FROM orders o 
        JOIN users u ON o.user_id = u.user_id 
        WHERE o.id = ?
    """
    result = db.execute_query(query, (order_id,))
    
    if result:
        order = result[0]
        
        # تحديد طريقة الدفع باللغة المناسبة
        payment_methods = {
            'ar': {
                'shamcash': 'شام كاش',
                'syriatel': 'سيرياتيل كاش', 
                'coinex': 'Coinex',
                'binance': 'Binance',
                'payeer': 'Payeer'
            },
            'en': {
                'shamcash': 'Sham Cash',
                'syriatel': 'Syriatel Cash',
                'coinex': 'Coinex', 
                'binance': 'Binance',
                'payeer': 'Payeer'
            }
        }
        
        payment_method = payment_methods[language].get(order[5], order[5])
        
        if language == 'ar':
            message = f"""📋 نسخة من طلبك
            
👤 الاسم: `{order[15]} {order[16] or ''}`
🆔 معرف المستخدم: `{order[1]}`

━━━━━━━━━━━━━━━
📦 تفاصيل الطلب:
📊 الكمية: {order[8]}
🔧 نوع البروكسي: {get_detailed_proxy_type(order[2], order[14] if len(order) > 14 else '')}
🌍 الدولة: {order[3]}
🏠 الولاية: {order[4]}

━━━━━━━━━━━━━━━
💳 تفاصيل الدفع:
💰 طريقة الدفع: {payment_method}
💵 قيمة الطلب: `{order[6]}$`

━━━━━━━━━━━━━━━
🔗 معرف الطلب: `{order[0]}`
📅 تاريخ الطلب: {order[9]}
📊 الحالة: ⏳ تحت المراجعة

يرجى الاحتفاظ بمعرف الطلب للمراجعة المستقبلية."""
        else:
            message = f"""📋 Copy of Your Order
            
👤 Name: `{order[15]} {order[16] or ''}`
🆔 User ID: `{order[1]}`

━━━━━━━━━━━━━━━
📦 Order Details:
📊 Quantity: {order[8]}
🔧 Proxy Type: {order[2]}
🌍 Country: {order[3]}
🏠 State: {order[4]}

━━━━━━━━━━━━━━━
💳 Payment Details:
💰 Payment Method: {payment_method}
💵 Order Value: `{order[6]}$`

━━━━━━━━━━━━━━━
🔗 Order ID: `{order[0]}`
📅 Order Date: {order[9]}
📊 Status: ⏳ Under Review

Please keep the order ID for future reference."""
        
        await context.bot.send_message(user_id, message, parse_mode='Markdown')

def create_admin_notification_message(order_id: str, user_id: int, proxy_type: str, country: str, state: str, payment_amount: float, language: str, quantity: int = 1, static_type: str = "") -> str:
    """إنشاء رسالة إشعار للأدمن عن طلب جديد"""
    try:
        # الحصول على بيانات المستخدم
        user = db.get_user(user_id)
        if not user:
            return f"❌ خطأ: لم يتم العثور على بيانات المستخدم {user_id}"
        
        # تنسيق نوع البروكسي للعرض
        proxy_display = {
            'static': 'بروكسي ستاتيك 🌐',
            'socks': 'بروكسي سوكس'
        }.get(proxy_type, proxy_type)
        
        # تنسيق نوع الستاتيك إذا كان موجوداً
        static_display = ""
        if static_type:
            static_display = f"\n🔧 النوع: {static_type}"
        
        # تنظيف اسم المستخدم من الرموز الخاصة
        username = user[1] or 'غير محدد'
        if username != 'غير محدد':
            # إزالة الرموز التي قد تتعارض مع Markdown
            username = username.replace('_', '\\_').replace('*', '\\*').replace('[', '\\[').replace(']', '\\]').replace('(', '\\(').replace(')', '\\)')
        
        message = f"""🔔 طلب {proxy_display} جديد!

👤 الاسم: {user[2]} {user[3] or ''}
📱 اسم المستخدم: {username}
🆔 معرف المستخدم: {user_id}

━━━━━━━━━━━━━━━
📦 تفاصيل الطلب:
🌍 الدولة: {country}
🏛️ الولاية: {state}
📊 الكمية: {quantity}{static_display}
💰 السعر: {payment_amount:.2f}$

━━━━━━━━━━━━━━━
🔗 معرف الطلب: {order_id}
📅 التاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

⚡ انقر على الزر أدناه لمعالجة الطلب"""
        
        return message
        
    except Exception as e:
        logger.error(f"Error creating admin notification message: {e}")
        return f"❌ خطأ في إنشاء رسالة الإشعار للطلب: {order_id}"

async def send_admin_notification(context: ContextTypes.DEFAULT_TYPE, order_id: str, payment_proof: str = None) -> None:
    """إرسال إشعار للآدمن بطلب جديد (يستخدم ACTIVE_ADMINS و ADMIN_CHAT_ID)"""
    global ACTIVE_ADMINS, ADMIN_CHAT_ID
    
    # جمع معرفات الآدمن من كلا المصدرين
    admin_ids = set()
    
    if ACTIVE_ADMINS:
        admin_ids.update(ACTIVE_ADMINS)
    
    if ADMIN_CHAT_ID:
        admin_ids.add(ADMIN_CHAT_ID)
    
    # إذا لم يكن هناك آدمن نشطين، جرب الحصول عليهم من قاعدة البيانات
    if not admin_ids:
        try:
            admin_query = "SELECT value FROM settings WHERE key = 'admin_chat_id'"
            admin_result = db.execute_query(admin_query)
            if admin_result and admin_result[0][0]:
                admin_ids.add(int(admin_result[0][0]))
                print(f"✅ تم الحصول على آدمن من قاعدة البيانات: {admin_result[0][0]}")
        except Exception as e:
            print(f"⚠️ خطأ في الحصول على آدمن من قاعدة البيانات: {e}")
    
    if not admin_ids:
        print(f"⚠️ لا يوجد آدمن متاح - لا يمكن إرسال إشعار للطلب: {order_id}")
        return
    
    # جلب تفاصيل الطلب لإضافتها للإشعار
    order_query = "SELECT quantity, proxy_type, country FROM orders WHERE id = ?"
    order_result = db.execute_query(order_query, (order_id,))
    
    if order_result:
        quantity, proxy_type, country = order_result[0]
        message = f"🔔 لديك طلب جديد\n\n🆔 معرف الطلب: `{order_id}`\n📊 الكمية: {quantity}\n🔧 النوع: {proxy_type}\n🌍 الدولة: {country}"
    else:
        message = f"🔔 لديك طلب جديد\n\n🆔 معرف الطلب: `{order_id}`"
    
    keyboard = [[InlineKeyboardButton("📋 عرض الطلب", callback_data=f"view_order_{order_id}")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # إرسال الإشعار لجميع الآدمن المتاحين
    sent_count = 0
    for admin_id in admin_ids:
        try:
            await context.bot.send_message(
                admin_id, 
                message, 
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            sent_count += 1
            print(f"✅ تم إرسال إشعار للأدمن {admin_id} للطلب: {order_id}")
        except Exception as e:
            logger.error(f"Error sending admin notification to admin {admin_id}: {e}")
            print(f"❌ فشل إرسال إشعار للأدمن {admin_id}: {e}")
    
    if sent_count > 0:
        print(f"✅ تم إرسال إشعار ل {sent_count} آدمن للطلب: {order_id}")
    else:
        print(f"⚠️ فشل إرسال الإشعار لجميع الآدمن للطلب: {order_id}")

async def send_admin_notification_with_details(context: ContextTypes.DEFAULT_TYPE, order_id: str, user_id: int, proxy_type: str, country: str, state: str, payment_amount: float, language: str, quantity: int, static_type: str = "") -> None:
    """إرسال إشعار للآدمن النشطين عن طلب بروكسي جديد مع جميع التفاصيل"""
    try:
        global ACTIVE_ADMINS, ADMIN_CHAT_ID
        
        # جمع معرفات الآدمن من كلا المصدرين
        admin_ids = set()
        
        if ACTIVE_ADMINS:
            admin_ids.update(ACTIVE_ADMINS)
        
        if ADMIN_CHAT_ID:
            admin_ids.add(ADMIN_CHAT_ID)
        
        # إذا لم يكن هناك آدمن نشطين، جرب الحصول عليهم من قاعدة البيانات
        if not admin_ids:
            try:
                admin_query = "SELECT value FROM settings WHERE key = 'admin_chat_id'"
                admin_result = db.execute_query(admin_query)
                if admin_result and admin_result[0][0]:
                    admin_ids.add(int(admin_result[0][0]))
                    print(f"✅ تم الحصول على آدمن من قاعدة البيانات: {admin_result[0][0]}")
            except Exception as e:
                print(f"⚠️ خطأ في الحصول على آدمن من قاعدة البيانات: {e}")
        
        if not admin_ids:
            print(f"⚠️ لا يوجد آدمن متاح - لا يمكن إرسال إشعار للطلب: {order_id}")
            return
        
        # إنشاء رسالة الإشعار باستخدام create_admin_notification_message
        admin_message = create_admin_notification_message(
            order_id, user_id, proxy_type, country, 
            state, payment_amount, language, quantity, static_type
        )
        
        keyboard = [[InlineKeyboardButton("⚡ معالجة الطلب", callback_data=f"process_{order_id}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # إرسال الإشعار لجميع الآدمن المتاحين
        sent_count = 0
        for admin_id in admin_ids:
            try:
                await context.bot.send_message(
                    admin_id,
                    admin_message,
                    reply_markup=reply_markup,
                    parse_mode='Markdown'
                )
                sent_count += 1
                print(f"✅ تم إرسال إشعار للأدمن {admin_id} للطلب: {order_id}")
            except Exception as e:
                logger.error(f"Error sending notification to admin {admin_id}: {e}")
                print(f"❌ فشل إرسال إشعار للأدمن {admin_id}: {e}")
        
        if sent_count > 0:
            print(f"✅ تم إرسال إشعار ل {sent_count} آدمن للطلب: {order_id}")
        else:
            print(f"⚠️ فشل إرسال الإشعار لجميع الآدمن للطلب: {order_id}")
            
    except Exception as e:
        logger.error(f"Error sending admin notification with details for order {order_id}: {e}")
        print(f"❌ خطأ في إرسال إشعار مفصل للأدمن: {e}")

async def handle_view_order_details(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """عرض تفاصيل الطلب مع التوثيق عند الضغط على زر عرض الطلب"""
    query = update.callback_query
    await query.answer()
    
    order_id = query.data.replace("view_order_", "")
    
    # الحصول على تفاصيل الطلب
    order_query = """
        SELECT o.*, u.first_name, u.last_name, u.username 
        FROM orders o 
        JOIN users u ON o.user_id = u.user_id 
        WHERE o.id = ?
    """
    result = db.execute_query(order_query, (order_id,))
    
    if not result:
        await query.edit_message_text("❌ لم يتم العثور على الطلب")
        return
    
    order = result[0]
    
    # تحديد طريقة الدفع باللغة العربية
    payment_methods_ar = {
        'shamcash': 'شام كاش',
        'syriatel': 'سيرياتيل كاش',
        'coinex': 'Coinex',
        'binance': 'Binance',
        'payeer': 'Payeer'
    }
    
    payment_method_ar = payment_methods_ar.get(order[5], order[5])
    
    message = f"""📋 تفاصيل الطلب مع التوثيق

👤 الاسم: {order[14]} {order[15] or ''}
📱 اسم المستخدم: @{order[16] or 'غير محدد'}
🆔 معرف المستخدم: {order[1]}

━━━━━━━━━━━━━━━
📦 تفاصيل الطلب:
📊 الكمية: {order[8]}
🔧 نوع البروكسي: {get_detailed_proxy_type(order[2], order[14] if len(order) > 14 else '')}
🌍 الدولة: {order[3]}
🏠 الولاية: {order[4]}

━━━━━━━━━━━━━━━
💳 تفاصيل الدفع:
💰 طريقة الدفع: {payment_method_ar}
💵 قيمة الطلب: `{order[6]}$`
📄 إثبات الدفع: {"✅ مرفق" if order[7] else "❌ غير مرفق"}

━━━━━━━━━━━━━━━
🔗 معرف الطلب: `{order_id}`
📅 تاريخ الطلب: {order[9]}
📊 الحالة: ⏳ معلق"""

    # إنشاء أزرار الإجراءات
    keyboard = [
        [InlineKeyboardButton("🔧 معالجة الطلب", callback_data=f"process_{order_id}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')
    
    # إرسال إثبات الدفع كرد على رسالة الطلب إذا كان موجوداً
    if order[7]:  # payment_proof
        try:
            if order[7].startswith("photo:"):
                file_id = order[7].replace("photo:", "")
                await context.bot.send_photo(
                    update.effective_chat.id,
                    photo=file_id,
                    caption=f"📸 إثبات دفع للطلب بمعرف: `{order_id}`",
                    parse_mode='Markdown',
                    reply_to_message_id=query.message.message_id
                )
            elif order[7].startswith("text:"):
                text_proof = order[7].replace("text:", "")
                await context.bot.send_message(
                    update.effective_chat.id,
                    f"📝 إثبات دفع للطلب بمعرف: `{order_id}`\n\nالنص:\n{text_proof}",
                    parse_mode='Markdown',
                    reply_to_message_id=query.message.message_id
                )
        except Exception as e:
            print(f"خطأ في إرسال إثبات الدفع: {e}")

async def handle_view_pending_order_details(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """عرض تفاصيل الطلب المعلق مع التوثيق"""
    query = update.callback_query
    await query.answer()
    
    order_id = query.data.replace("view_pending_order_", "")
    
    # فحص نوع الطلب أولاً
    proxy_type_query = "SELECT proxy_type FROM orders WHERE id = ?"
    proxy_type_result = db.execute_query(proxy_type_query, (order_id,))
    
    if proxy_type_result and proxy_type_result[0][0] == 'balance_recharge':
        # إذا كان طلب شحن رصيد، وجه إلى الدالة المناسبة
        # إنشاء update جديد مع callback_data الصحيح للتوافق مع معالج شحن الرصيد
        # تطبيق callback_data جديد دون تعديل الأصلي
        recharge_callback_data = f"view_recharge_{order_id}"
        
        # استدعاء المعالج مباشرة مع إرسال order_id
        await handle_view_recharge_details_with_id(update, context, order_id, answered=True)
        return
    
    # الحصول على تفاصيل الطلب للطلبات العادية
    order_query = """
        SELECT o.*, u.first_name, u.last_name, u.username 
        FROM orders o 
        JOIN users u ON o.user_id = u.user_id 
        WHERE o.id = ?
    """
    result = db.execute_query(order_query, (order_id,))
    
    if not result:
        await query.edit_message_text("❌ لم يتم العثور على الطلب")
        return
    
    order = result[0]
    
    # التحقق من طول البيانات لتجنب خطأ tuple index out of range
    # جدول orders يحتوي على 14 حقل + 3 حقول من users = 17 حقل إجمالي
    if len(order) < 17:
        await query.edit_message_text("❌ بيانات الطلب غير كاملة. يرجى المحاولة مرة أخرى.")
        return
    
    # تحديد طريقة الدفع باللغة العربية
    payment_methods_ar = {
        'shamcash': 'شام كاش',
        'syriatel': 'سيرياتيل كاش',
        'coinex': 'Coinex',
        'binance': 'Binance',
        'payeer': 'Payeer'
    }
    
    payment_method_ar = payment_methods_ar.get(order[5] if len(order) > 5 else '', 'غير محدد')
    
    # استخراج البيانات بطريقة آمنة
    user_first_name = order[15] if len(order) > 15 else 'غير محدد'
    user_last_name = order[16] if len(order) > 16 else ''
    username = order[17] if len(order) > 17 else 'غير محدد'
    quantity = order[8] if len(order) > 8 else 'غير محدد'
    static_type = order[14] if len(order) > 14 else ''
    
    message = f"""📋 تفاصيل الطلب الكاملة مع التوثيق

👤 الاسم: `{user_first_name} {user_last_name}`
📱 اسم المستخدم: @{username}
🆔 معرف المستخدم: `{order[1]}`

━━━━━━━━━━━━━━━
📦 تفاصيل الطلب:
📊 الكمية: {quantity}
🔧 نوع البروكسي: {get_detailed_proxy_type(order[2], static_type)}
🌍 الدولة: {order[3]}
🏠 الولاية: {order[4]}

━━━━━━━━━━━━━━━
💳 تفاصيل الدفع:
💰 طريقة الدفع: {payment_method_ar}
💵 قيمة الطلب: `{order[6]}$`
📄 إثبات الدفع: {"✅ مرفق" if order[7] else "❌ غير مرفق"}

━━━━━━━━━━━━━━━
🔗 معرف الطلب: {order_id}
📅 تاريخ الطلب: {order[9]}
📊 الحالة: ⏳ معلق"""

    # إنشاء أزرار الإجراءات (معالجة مع سؤال التحقق من الدفع)
    keyboard = [
        [InlineKeyboardButton("✅ معالجة الطلب", callback_data=f"process_{order_id}")],
        [InlineKeyboardButton("🔙 العودة للطلبات المعلقة", callback_data="back_to_pending_orders")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')
    
    # إرسال إثبات الدفع كرد على رسالة الطلب إذا كان موجوداً
    if order[7]:  # payment_proof
        try:
            if order[7].startswith("photo:"):
                file_id = order[7].replace("photo:", "")
                await context.bot.send_photo(
                    update.effective_chat.id,
                    photo=file_id,
                    caption=f"📸 إثبات دفع للطلب بمعرف: `{order_id}`",
                    parse_mode='Markdown',
                    reply_to_message_id=query.message.message_id
                )
            elif order[7].startswith("text:"):
                text_proof = order[7].replace("text:", "")
                await context.bot.send_message(
                    update.effective_chat.id,
                    f"📝 إثبات دفع للطلب بمعرف: `{order_id}`\n\nالنص:\n{text_proof}",
                    parse_mode='Markdown',
                    reply_to_message_id=query.message.message_id
                )
        except Exception as e:
            print(f"خطأ في إرسال إثبات الدفع: {e}")

async def handle_referrals(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالجة قسم الإحالات"""
    user_id = update.effective_user.id
    language = get_user_language(user_id)
    
    # إنشاء رابط الإحالة
    try:
        bot_info = await context.bot.get_me()
        bot_username = bot_info.username
    except:
        bot_username = "your_bot"  # fallback if bot info fails
    
    referral_link = f"https://t.me/{bot_username}?start={user_id}"
    
    # الحصول على رصيد الإحالة
    user = db.get_user(user_id)
    referral_balance = user[5] if user else 0.0
    
    # عدد الإحالات
    query = "SELECT COUNT(*) FROM referrals WHERE referrer_id = ?"
    referral_count = db.execute_query(query, (user_id,))[0][0]
    
    if language == 'ar':
        message = f"""👥 نظام الإحالات

🔗 رابط الإحالة الخاص بك:
`{referral_link}`

💰 رصيدك: `{referral_balance:.2f}$`
👥 عدد إحالاتك: `{referral_count}`

━━━━━━━━━━━━━━━
شارك رابطك واحصل على {get_referral_percentage()}% من كل عملية شراء!
💡 يتم إضافة المكافأة عند كل عملية شراء ناجحة يقوم بها المُحال
الحد الأدنى للسحب: `1.0$`"""
    else:
        message = f"""👥 Referral System

🔗 Your referral link:
`{referral_link}`

💰 Your balance: `{referral_balance:.2f}$`
👥 Your referrals: `{referral_count}`

━━━━━━━━━━━━━━━
Share your link and earn {get_referral_percentage()}% from every purchase!
💡 Bonus is added for every successful purchase made by referred user
Minimum withdrawal: `1.0$`"""
    
    keyboard = [
        [InlineKeyboardButton("💸 سحب الرصيد" if language == 'ar' else "💸 Withdraw Balance", callback_data="withdraw_balance")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(message, reply_markup=reply_markup, parse_mode='Markdown')

# دوال معالجة قائمة الرصيد الجديدة
async def handle_balance_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالجة قائمة الرصيد الرئيسية"""
    user_id = update.effective_user.id
    language = get_user_language(user_id)
    
    # إرسال قائمة الرصيد
    balance_keyboard = create_balance_keyboard(language)
    await update.message.reply_text(
        MESSAGES[language]['balance_menu_title'],
        reply_markup=balance_keyboard
    )

async def handle_my_balance(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالجة عرض الرصيد الحالي"""
    user_id = update.effective_user.id
    language = get_user_language(user_id)
    
    # الحصول على الرصيد
    balance_data = db.get_user_balance(user_id)
    
    # عرض الرصيد المفصل
    message = MESSAGES[language]['current_balance'].format(
        charged_balance=balance_data['charged_balance'],
        referral_balance=balance_data['referral_balance'],
        total_balance=balance_data['total_balance']
    )
    
    await update.message.reply_text(message, parse_mode='Markdown')

async def handle_recharge_balance(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالجة طلب شحن الرصيد"""
    user_id = update.effective_user.id
    language = get_user_language(user_id)
    
    # الحصول على سعر النقطة
    credit_price = db.get_credit_price()
    
    # عرض رسالة طلب شحن الرصيد
    message = MESSAGES[language]['recharge_request'].format(credit_price=credit_price)
    
    # إنشاء زر الرجوع
    if language == 'ar':
        keyboard = [[InlineKeyboardButton("↩️ رجوع للقائمة الرئيسية", callback_data="back_to_main_from_recharge")]]
    else:
        keyboard = [[InlineKeyboardButton("↩️ Back to Main Menu", callback_data="back_to_main_from_recharge")]]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(message, parse_mode='Markdown')
    await update.message.reply_text(MESSAGES[language]['enter_recharge_amount'], reply_markup=reply_markup)
    
    # تعيين حالة انتظار المبلغ
    context.user_data['waiting_for_recharge_amount'] = True

async def handle_balance_referrals(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالجة الإحالات من داخل قائمة الرصيد"""
    await handle_referrals(update, context)

async def handle_back_to_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """العودة للقائمة الرئيسية من قائمة الرصيد"""
    user_id = update.effective_user.id
    language = get_user_language(user_id)
    
    # إرسال القائمة الرئيسية
    main_keyboard = create_main_user_keyboard(language)
    await update.message.reply_text(
        MESSAGES[language]['welcome'],
        reply_markup=main_keyboard
    )

async def handle_recharge_amount_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالجة إدخال مبلغ الشحن"""
    user_id = update.effective_user.id
    language = get_user_language(user_id)
    
    try:
        amount = float(update.message.text)
        if amount <= 0:
            await update.message.reply_text(MESSAGES[language]['invalid_recharge_amount'])
            return
        
        # حساب النقاط المتوقعة
        credit_price = db.get_credit_price()
        expected_credits = amount / credit_price
        
        # حفظ بيانات الطلب في الذاكرة فقط (بدون حفظ في قاعدة البيانات حتى الآن)
        order_id = generate_order_id()
        context.user_data['recharge_order_id'] = order_id
        context.user_data['recharge_amount'] = amount
        context.user_data['expected_credits'] = expected_credits
        context.user_data['waiting_for_recharge_amount'] = False
        context.user_data['waiting_for_recharge_payment_method'] = True
        
        # ملاحظة: لن يتم حفظ الطلب في قاعدة البيانات حتى يتم إرسال إثبات الدفع
        
        # عرض طرق الدفع
        if language == 'ar':
            keyboard = [
                [InlineKeyboardButton("💳 شام كاش", callback_data="recharge_payment_shamcash")],
                [InlineKeyboardButton("💳 سيرياتيل كاش", callback_data="recharge_payment_syriatel")],
                [InlineKeyboardButton("🪙 Coinex", callback_data="recharge_payment_coinex")],
                [InlineKeyboardButton("🪙 Binance", callback_data="recharge_payment_binance")],
                [InlineKeyboardButton("🪙 Payeer", callback_data="recharge_payment_payeer")],
                [InlineKeyboardButton("↩️ رجوع", callback_data="back_to_amount")]
            ]
            message = f"💰 مبلغ الشحن: {amount}$\n💎 النقاط المتوقعة: {expected_credits:.1f}\n\n💳 اختر طريقة الدفع المفضلة:"
        else:
            keyboard = [
                [InlineKeyboardButton("💳 Sham Cash", callback_data="recharge_payment_shamcash")],
                [InlineKeyboardButton("💳 Syriatel Cash", callback_data="recharge_payment_syriatel")],
                [InlineKeyboardButton("🪙 Coinex", callback_data="recharge_payment_coinex")],
                [InlineKeyboardButton("🪙 Binance", callback_data="recharge_payment_binance")],
                [InlineKeyboardButton("🪙 Payeer", callback_data="recharge_payment_payeer")],
                [InlineKeyboardButton("↩️ Back", callback_data="back_to_amount")]
            ]
            message = f"💰 Recharge Amount: {amount}$\n💎 Expected Points: {expected_credits:.1f}\n\n💳 Choose your preferred payment method:"
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(message, reply_markup=reply_markup)
        
    except ValueError:
        await update.message.reply_text(MESSAGES[language]['invalid_recharge_amount'])

async def handle_recharge_payment_method_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالجة اختيار طريقة الدفع لشحن الرصيد"""
    try:
        query = update.callback_query
        user_id = update.effective_user.id
        language = get_user_language(user_id)
        
        await query.answer()
        
        # استخراج طريقة الدفع المختارة
        payment_method = query.data.replace("recharge_payment_", "")
        context.user_data['recharge_payment_method'] = payment_method
        context.user_data['waiting_for_recharge_payment_method'] = False
        context.user_data['waiting_for_recharge_proof'] = True
        
        # الحصول على المبلغ والنقاط المتوقعة وسعر الكريديت
        amount = context.user_data.get('recharge_amount', 0)
        expected_credits = context.user_data.get('expected_credits', 0)
        credit_price = db.get_credit_price()
        
        # إعداد بيانات طريقة الدفع المختارة
        payment_details = {
            'shamcash': {
                'ar': '💳 شام كاش\n\nالحساب: cc849f22d5117db0b8fe5667e6d4b758',
                'en': '💳 Sham Cash\n\nAccount: cc849f22d5117db0b8fe5667e6d4b758'
            },
            'syriatel': {
                'ar': '💳 سيرياتيل كاش\n\nالحساب: 55973911\nأو: 14227865',
                'en': '💳 Syriatel Cash\n\nAccount: 55973911\nOr: 14227865'
            },
            'coinex': {
                'ar': '🪙 Coinex\n\nالبريد: sohilskaf123@gmail.com',
                'en': '🪙 Coinex\n\nEmail: sohilskaf123@gmail.com'
            },
            'binance': {
                'ar': '🪙 Binance\n\nالمعرف: 1160407924',
                'en': '🪙 Binance\n\nID: 1160407924'
            },
            'payeer': {
                'ar': '🪙 Payeer\n\nالحساب: P1114452356',
                'en': '🪙 Payeer\n\nAccount: P1114452356'
            }
        }
        
        # بناء الرسالة
        if language == 'ar':
            message = f"""💳 شحن رصيد
            
💰 المبلغ: ${amount:.2f}
💎 النقاط المتوقعة: {expected_credits:.1f}
💵 سعر الكريديت: ${credit_price:.2f}

━━━━━━━━━━━━━━━
{payment_details.get(payment_method, {}).get('ar', '')}

━━━━━━━━━━━━━━━
📩 يرجى إرسال إثبات الدفع (صورة فقط)
⏱️ سيتم مراجعة الطلب من قبل الأدمن"""
        else:
            message = f"""💳 Balance Recharge
            
💰 Amount: ${amount:.2f}
💎 Expected Points: {expected_credits:.1f}
💵 Credit Price: ${credit_price:.2f}

━━━━━━━━━━━━━━━
{payment_details.get(payment_method, {}).get('en', '')}

━━━━━━━━━━━━━━━
📩 Please send payment proof (image only)
⏱️ Admin will review the request"""
        
        # إضافة زر رجوع
        if language == 'ar':
            keyboard = [[InlineKeyboardButton("↩️ تغيير طريقة الدفع", callback_data="back_to_payment_method")]]
        else:
            keyboard = [[InlineKeyboardButton("↩️ Change Payment Method", callback_data="back_to_payment_method")]]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(message, reply_markup=reply_markup)
        
    except Exception as e:
        logger.error(f"Error in handle_recharge_payment_method_selection: {e}")
        await query.message.reply_text("❌ حدث خطأ، يرجى المحاولة مرة أخرى.")

async def handle_recharge_payment_proof(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالجة إثبات دفع الشحن"""
    user_id = update.effective_user.id
    language = get_user_language(user_id)
    
    order_id = context.user_data.get('recharge_order_id')
    amount = context.user_data.get('recharge_amount')
    expected_credits = context.user_data.get('expected_credits')
    payment_method = context.user_data.get('recharge_payment_method')
    
    if not order_id:
        await update.message.reply_text("❌ خطأ في النظام. يرجى إعادة المحاولة.")
        return
    
    # معالجة إثبات الدفع (صورة فقط مطلوبة)
    if not update.message.photo:
        if language == 'ar':
            await update.message.reply_text("❌ يرجى إرسال صورة إثبات الدفع فقط")
        else:
            await update.message.reply_text("❌ Please send payment proof image only")
        return
    
    file_id = update.message.photo[-1].file_id
    payment_proof = f"photo:{file_id}"
    
    print(f"📸 تم استلام إثبات دفع الشحن (صورة) للطلب: {order_id}")
    
    # إرسال نسخة للمستخدم
    if language == 'ar':
        caption = f"📸 إثبات دفع شحن الرصيد\n\n🆔 معرف الطلب: {order_id}\n💰 المبلغ: {amount}$\n💎 النقاط المتوقعة: {expected_credits:.1f}\n💳 طريقة الدفع: {payment_method}\n\n✅ تم حفظ إثبات الدفع بنجاح"
    else:
        caption = f"📸 Balance Recharge Payment Proof\n\n🆔 Order ID: {order_id}\n💰 Amount: {amount}$\n💎 Expected Points: {expected_credits:.1f}\n💳 Payment Method: {payment_method}\n\n✅ Payment proof saved successfully"
    
    await update.message.reply_photo(
        photo=file_id,
        caption=caption,
        parse_mode='Markdown'
    )
    
    # الآن إنشاء الطلب في قاعدة البيانات مع إثبات الدفع (فقط بعد استلام الإثبات)
    db.create_recharge_order(order_id, user_id, amount, expected_credits)
    
    # تحديث الطلب بإثبات الدفع وطريقة الدفع
    db.execute_query(
        "UPDATE orders SET payment_proof = ?, payment_method = ?, status = 'pending' WHERE id = ? AND proxy_type = 'balance_recharge'",
        (payment_proof, payment_method, order_id)
    )
    print(f"💾 تم إنشاء الطلب وحفظ إثبات الدفع في قاعدة البيانات للطلب: {order_id}")
    
    # إرسال رسالة التأكيد
    message = MESSAGES[language]['recharge_order_created'].format(
        order_id=order_id,
        amount=amount,
        points=expected_credits
    )
    await update.message.reply_text(message, parse_mode='Markdown')
    print(f"✅ تم إرسال رسالة التأكيد للمستخدم لطلب الشحن: {order_id}")
    
    # إرسال إشعار للأدمن
    try:
        print(f"🔔 محاولة إرسال إشعار للأدمن لطلب الشحن: {order_id}")
        await send_recharge_admin_notification(context, order_id, user_id, amount, expected_credits, payment_proof, payment_method)
        print(f"✅ تم إرسال إشعار الأدمن بنجاح لطلب الشحن: {order_id}")
    except Exception as e:
        print(f"⚠️ خطأ في إرسال إشعار الأدمن لطلب الشحن {order_id}: {e}")
    
    # تنظيف البيانات المؤقتة
    context.user_data.pop('recharge_order_id', None)
    context.user_data.pop('recharge_amount', None)
    context.user_data.pop('expected_credits', None)
    context.user_data.pop('waiting_for_recharge_proof', None)
    
    # العودة للقائمة الرئيسية
    await handle_back_to_main_menu(update, context)

async def handle_back_to_amount(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالجة الرجوع لإدخال المبلغ"""
    try:
        query = update.callback_query
        user_id = update.effective_user.id
        language = get_user_language(user_id)
        
        await query.answer()
        
        # حذف البيانات المؤقتة للعودة لإدخال المبلغ
        context.user_data.pop('recharge_order_id', None)
        context.user_data.pop('recharge_amount', None)
        context.user_data.pop('expected_credits', None)
        context.user_data.pop('waiting_for_recharge_payment_method', None)
        context.user_data['waiting_for_recharge_amount'] = True
        
        # عرض رسالة إدخال المبلغ مرة أخرى
        credit_price = db.get_credit_price()
        message = MESSAGES[language]['recharge_request'].format(credit_price=credit_price)
        
        # إنشاء زر الرجوع
        if language == 'ar':
            keyboard = [[InlineKeyboardButton("↩️ رجوع للقائمة الرئيسية", callback_data="back_to_main_from_recharge")]]
        else:
            keyboard = [[InlineKeyboardButton("↩️ Back to Main Menu", callback_data="back_to_main_from_recharge")]]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(message, parse_mode='Markdown')
        await query.message.reply_text(MESSAGES[language]['enter_recharge_amount'], reply_markup=reply_markup)
        
    except Exception as e:
        logger.error(f"Error in handle_back_to_amount: {e}")
        await query.edit_message_text("❌ حدث خطأ، يرجى المحاولة مرة أخرى.")

async def handle_back_to_payment_method(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالجة الرجوع من صورة التأكيد إلى اختيار طريقة الدفع"""
    try:
        query = update.callback_query
        user_id = update.effective_user.id
        language = get_user_language(user_id)
        
        await query.answer()
        
        # استرجاع بيانات الطلب
        amount = context.user_data.get('recharge_amount')
        expected_credits = context.user_data.get('expected_credits')
        
        if not amount or not expected_credits:
            await query.edit_message_text("❌ خطأ في النظام. يرجى إعادة المحاولة.")
            return
        
        # إعادة تعيين الحالة
        context.user_data['waiting_for_recharge_proof'] = False
        context.user_data['waiting_for_recharge_payment_method'] = True
        context.user_data.pop('recharge_payment_method', None)
        
        # عرض طرق الدفع مرة أخرى
        if language == 'ar':
            keyboard = [
                [InlineKeyboardButton("💳 شام كاش", callback_data="recharge_payment_shamcash")],
                [InlineKeyboardButton("💳 سيرياتيل كاش", callback_data="recharge_payment_syriatel")],
                [InlineKeyboardButton("🪙 Coinex", callback_data="recharge_payment_coinex")],
                [InlineKeyboardButton("🪙 Binance", callback_data="recharge_payment_binance")],
                [InlineKeyboardButton("🪙 Payeer", callback_data="recharge_payment_payeer")],
                [InlineKeyboardButton("↩️ رجوع", callback_data="back_to_amount")]
            ]
            message = f"💰 مبلغ الشحن: {amount}$\n💎 النقاط المتوقعة: {expected_credits:.1f}\n\n💳 اختر طريقة الدفع المفضلة:"
        else:
            keyboard = [
                [InlineKeyboardButton("💳 Sham Cash", callback_data="recharge_payment_shamcash")],
                [InlineKeyboardButton("💳 Syriatel Cash", callback_data="recharge_payment_syriatel")],
                [InlineKeyboardButton("🪙 Coinex", callback_data="recharge_payment_coinex")],
                [InlineKeyboardButton("🪙 Binance", callback_data="recharge_payment_binance")],
                [InlineKeyboardButton("🪙 Payeer", callback_data="recharge_payment_payeer")],
                [InlineKeyboardButton("↩️ Back", callback_data="back_to_amount")]
            ]
            message = f"💰 Recharge Amount: {amount}$\n💎 Expected Points: {expected_credits:.1f}\n\n💳 Choose your preferred payment method:"
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(message, reply_markup=reply_markup)
        
    except Exception as e:
        logger.error(f"Error in handle_back_to_payment_method: {e}")
        await query.edit_message_text("❌ حدث خطأ، يرجى المحاولة مرة أخرى.")

async def handle_back_to_main_from_recharge(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالجة الرجوع للقائمة الرئيسية من شحن الرصيد"""
    try:
        query = update.callback_query
        user_id = update.effective_user.id
        language = get_user_language(user_id)
        
        await query.answer()
        
        # تنظيف جميع البيانات المؤقتة لشحن الرصيد
        context.user_data.pop('recharge_order_id', None)
        context.user_data.pop('recharge_amount', None)
        context.user_data.pop('expected_credits', None)
        context.user_data.pop('recharge_payment_method', None)
        context.user_data.pop('waiting_for_recharge_amount', None)
        context.user_data.pop('waiting_for_recharge_payment_method', None)
        context.user_data.pop('waiting_for_recharge_proof', None)
        
        # إرسال القائمة الرئيسية
        main_keyboard = create_main_user_keyboard(language)
        await query.edit_message_text(
            MESSAGES[language]['welcome'],
            reply_markup=main_keyboard
        )
        
    except Exception as e:
        logger.error(f"Error in handle_back_to_main_from_recharge: {e}")
        await query.edit_message_text("❌ حدث خطأ، يرجى المحاولة مرة أخرى.")

async def send_recharge_admin_notification(context, order_id: str, user_id: int, amount: float, expected_credits: float, payment_proof: str, payment_method: str = "غير محدد"):
    """إرسال إشعار للآدمن النشطين عن طلب شحن رصيد جديد"""
    try:
        global ACTIVE_ADMINS
        
        if not ACTIVE_ADMINS:
            return
        
        user = db.get_user(user_id)
        if not user:
            return
        
        # معالجة طريقة الدفع للعرض
        payment_method_display = {
            'shamcash': 'شام كاش 💳',
            'syriatel': 'سيرياتيل كاش 💳',
            'coinex': 'Coinex 🪙',
            'binance': 'Binance 🪙',
            'payeer': 'Payeer 🪙'
        }.get(payment_method, payment_method or 'غير محدد')
        
        # رسالة مختصرة للإشعار - بدون تفاصيل
        message = f"""🔔 طلب شحن رصيد جديد!

👤 {user[2]} {user[3] or ''} (@{user[1] or 'غير محدد'})
💰 ${amount:.2f} → {expected_credits:.2f} نقطة
🆔 `{order_id}`"""

        keyboard = [
            [InlineKeyboardButton("📋 عرض تفاصيل الطلب", callback_data=f"view_recharge_{order_id}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # إرسال الإشعار لجميع الآدمن النشطين
        for admin_id in ACTIVE_ADMINS:
            try:
                await context.bot.send_message(
                    admin_id,
                    message,
                    reply_markup=reply_markup,
                    parse_mode='Markdown'
                )
            except Exception as e:
                logger.error(f"Error sending recharge notification to admin {admin_id}: {e}")
    except Exception as e:
        logger.error(f"Error sending recharge admin notification: {e}")

async def handle_settings(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالجة الإعدادات"""
    user_id = update.effective_user.id
    language = get_user_language(user_id)
    
    keyboard = [
        [InlineKeyboardButton("🌐 العربية", callback_data="lang_ar"),
         InlineKeyboardButton("🌐 English", callback_data="lang_en")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "اختر اللغة / Choose Language:",
        reply_markup=reply_markup
    )

async def handle_about_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالجة أمر /about"""
    user_id = update.effective_user.id
    language = get_user_language(user_id)
    
    # رسالة حول البوت
    about_message = MESSAGES[language]['about_bot']
    
    # إنشاء زر لإظهار النافذة المنبثقة
    if language == 'ar':
        button_text = "🧑‍💻 معلومات المطور"
        popup_text = """🧑‍💻 معلومات المطور

📦 بوت بيع البروكسي وإدارة البروكسي
🔢 الإصدار: 1.0.0

━━━━━━━━━━━━━━━
👨‍💻 طُور بواسطة: Mohamad Zalaf

📞 معلومات الاتصال:
📱 تليجرام: @MohamadZalaf
📧 البريد الإلكتروني:
   • MohamadZalaf@outlook.com
   • Mohamadzalaf2017@gmail.com

━━━━━━━━━━━━━━━
© Mohamad Zalaf 2025"""
    else:
        button_text = "🧑‍💻 Developer Info"
        popup_text = """🧑‍💻 Developer Information

📦 Proxy Sales & Management Bot
🔢 Version: 1.0.0

━━━━━━━━━━━━━━━
👨‍💻 Developed by: Mohamad Zalaf

📞 Contact Information:
📱 Telegram: @MohamadZalaf
📧 Email:
   • MohamadZalaf@outlook.com
   • Mohamadzalaf2017@gmail.com

━━━━━━━━━━━━━━━
© Mohamad Zalaf 2025"""
    
    keyboard = [[InlineKeyboardButton(button_text, callback_data="developer_info")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # إرسال الرسالة مع الزر
    await update.message.reply_text(
        about_message, 
        parse_mode='Markdown',
        reply_markup=reply_markup
    )
    
    # حفظ النص المنبثق في context للاستخدام لاحقاً
    context.user_data['popup_text'] = popup_text

async def handle_reset_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالجة أمر /reset لإعادة تعيين حالة المستخدم"""
    user_id = update.effective_user.id
    
    # تنظيف شامل للبيانات المؤقتة مع الحفاظ على حالة الأدمن
    clean_user_data_preserve_admin(context)
    
    # إنهاء أي محادثات نشطة
    try:
        return ConversationHandler.END
    except:
        pass
    
    # إعادة توجيه المستخدم بناءً على نوعه
    if context.user_data.get('is_admin', False) or user_id in ACTIVE_ADMINS:
        await restore_admin_keyboard(context, update.effective_chat.id, "🔄 تم إعادة تعيين حالة الأدمن")
    else:
        await start(update, context)
    
    await force_reset_user_state(update, context)

async def handle_cleanup_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالجة أمر /cleanup لتنظيف العمليات المعلقة"""
    user_id = update.effective_user.id
    is_admin = context.user_data.get('is_admin', False) or user_id in ACTIVE_ADMINS
    
    try:
        # تنظيف البيانات المؤقتة أولاً مع الحفاظ على حالة الأدمن
        clean_user_data_preserve_admin(context)
        
        # إعادة توجيه المستخدم للحالة المناسبة
        if is_admin:
            await restore_admin_keyboard(context, update.effective_chat.id, "🧹 تم تنظيف العمليات بنجاح")
        else:
            await update.message.reply_text(
                "🧹 **تم تنظيف العمليات المعلقة بنجاح**\n\n"
                "✅ تم إزالة جميع البيانات المؤقتة\n"
                "✅ تم تنظيف المحادثات المعلقة\n"
                "✅ البوت جاهز للاستخدام بشكل طبيعي",
                parse_mode='Markdown'
            )
            # إعادة إرسال القائمة الرئيسية للمستخدم العادي
            await start(update, context)
    except Exception as e:
        await update.message.reply_text(
            "⚠️ حدث خطأ أثناء التنظيف\n"
            "يرجى استخدام /reset لإعادة تعيين كاملة"
        )

async def handle_status_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالجة أمر /status لعرض حالة المستخدم الحالية"""
    user_id = update.effective_user.id
    
    # جمع معلومات الحالة
    user_data_keys = list(context.user_data.keys())
    is_admin = context.user_data.get('is_admin', False) or user_id in ACTIVE_ADMINS
    
    # تحديد العمليات النشطة
    active_operations = []
    
    if 'processing_order_id' in context.user_data:
        active_operations.append(f"🔄 معالجة طلب: {context.user_data['processing_order_id']}")
    
    if 'proxy_type' in context.user_data:
        active_operations.append(f"📦 طلب بروكسي: {context.user_data['proxy_type']}")
    
    if 'waiting_for' in context.user_data:
        active_operations.append(f"⏳ انتظار إدخال: {context.user_data['waiting_for']}")
    
    if 'broadcast_type' in context.user_data:
        active_operations.append(f"📢 إعداد بث: {context.user_data['broadcast_type']}")
    
    # إنشاء رسالة الحالة
    status_message = f"📊 **حالة المستخدم**\n\n"
    status_message += f"👤 المعرف: `{user_id}`\n"
    status_message += f"🔧 نوع المستخدم: {'أدمن' if is_admin else 'مستخدم عادي'}\n"
    status_message += f"💾 عدد البيانات المؤقتة: {len(user_data_keys)}\n\n"
    
    if active_operations:
        status_message += "🔄 **العمليات النشطة:**\n"
        for op in active_operations:
            status_message += f"• {op}\n"
    else:
        status_message += "✅ **لا توجد عمليات نشطة**\n"
    
    status_message += "\n📋 **الأوامر المتاحة:**\n"
    status_message += "• `/reset` - إعادة تعيين كاملة\n"
    status_message += "• `/cleanup` - تنظيف العمليات المعلقة\n"
    status_message += "• `/start` - العودة للقائمة الرئيسية"
    
    await update.message.reply_text(status_message, parse_mode='Markdown')

async def handle_language_change(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالجة تغيير اللغة"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    is_admin = context.user_data.get('is_admin', False)
    
    if query.data == "lang_ar":
        new_language = "ar"
        if is_admin:
            message = "تم تغيير اللغة إلى العربية ✅"
        else:
            message = """تم تغيير اللغة إلى العربية ✅
يرجى استخدام الأمر /start لإعادة تحميل القوائم

Language changed to Arabic ✅  
Please use /start command to reload menus"""
    else:
        new_language = "en"
        if is_admin:
            message = "Language changed to English ✅"
        else:
            message = """Language changed to English ✅
Please use /start command to reload menus

تم تغيير اللغة إلى الإنجليزية ✅
يرجى استخدام الأمر /start لإعادة تحميل القوائم"""
    
    db.update_user_language(user_id, new_language)
    db.log_action(user_id, "language_change", new_language)
    
    await query.edit_message_text(message)
    
    # إذا كان آدمن، استعادة كيبورد الآدمن
    if is_admin:
        await restore_admin_keyboard(context, user_id, "تم تحديث اللغة ✅" if new_language == 'ar' else "Language updated ✅")

async def handle_user_quantity_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالجة اختيار الكمية من قبل المستخدم"""
    try:
        query = update.callback_query
        user_id = update.effective_user.id
        
        # تسجيل مفصل لتتبع المشكلة
        logger.info(f"=== QUANTITY SELECTION START ===")
        logger.info(f"User ID: {user_id}")
        logger.info(f"Query data: {query.data}")
        logger.info(f"Current user_data: {context.user_data}")
        
        # تسجيل الإجراء
        logger.info(f"User {user_id} selected quantity: {query.data}")
        
        try:
            await query.answer()
        except Exception as answer_error:
            logger.warning(f"Failed to answer quantity callback for user {user_id}: {answer_error}")
        
        language = get_user_language(user_id)
        
        if query.data == "quantity_one_socks":
            logger.info(f"Processing ONE SOCKS PROXY for user {user_id}")
            
            # فحص فوري لحالة الخدمة
            if not db.get_service_status('socks', 'single'):
                if language == 'ar':
                    await query.edit_message_text("❌ خدمة السوكس الواحد غير متاحة حالياً\n\nيرجى اختيار خدمة أخرى أو المحاولة لاحقاً.")
                else:
                    await query.edit_message_text("❌ Single socks service is currently unavailable\n\nPlease choose another service or try again later.")
                return
            
            # الحصول على السعر الفعلي من قاعدة البيانات
            socks_prices = get_socks_prices()
            single_price = float(socks_prices.get('single_proxy', '0.15'))
            
            context.user_data['quantity'] = '1'  # كمية واحدة
            context.user_data['proxy_type'] = 'socks'
            context.user_data['socks_price'] = single_price
            # الانتقال لاختيار الدولة
            await show_country_selection_for_user(query, context, language)
            logger.info(f"=== QUANTITY SELECTION SUCCESS (one socks) ===")
            
        elif query.data == "quantity_two_socks":
            logger.info(f"Processing TWO SOCKS PROXIES for user {user_id}")
            
            # فحص فوري لحالة الخدمة
            if not db.get_service_status('socks', 'package_2'):
                if language == 'ar':
                    await query.edit_message_text("❌ خدمة السوكس اثنان غير متاحة حالياً\n\nيرجى اختيار خدمة أخرى أو المحاولة لاحقاً.")
                else:
                    await query.edit_message_text("❌ Two socks service is currently unavailable\n\nPlease choose another service or try again later.")
                return
            
            # الحصول على السعر الفعلي من قاعدة البيانات
            socks_prices = get_socks_prices()
            double_price = float(socks_prices.get('double_proxy', '0.25'))
            
            context.user_data['quantity'] = 1  # باكج واحد يحتوي على 2 بروكسي
            context.user_data['proxy_type'] = 'socks'
            context.user_data['socks_price'] = double_price
            # الانتقال لاختيار الدولة
            await show_country_selection_for_user(query, context, language)
            logger.info(f"=== QUANTITY SELECTION SUCCESS (two socks) ===")
            
        elif query.data == "quantity_verizon_static":
            logger.info(f"Processing RESIDENTIAL VERIZON for user {user_id}")
            
            # فحص فوري لحالة الخدمة
            if not db.get_service_status('static', 'monthly_verizon'):
                if language == 'ar':
                    await query.edit_message_text("❌ خدمة ريزيدنتال ڤيرايزون غير متاحة حالياً\n\nيرجى اختيار خدمة أخرى أو المحاولة لاحقاً.")
                else:
                    await query.edit_message_text("❌ Residential Verizon service is currently unavailable\n\nPlease choose another service or try again later.")
                return
            
            context.user_data['quantity'] = '5'
            context.user_data['static_type'] = 'residential_verizon'
            # عرض دولة أمريكا
            if language == 'ar':
                keyboard = [
                    [InlineKeyboardButton("🇺🇸 الولايات المتحدة", callback_data="country_US_verizon")],
                    [InlineKeyboardButton("🔙 رجوع", callback_data="cancel_user_proxy_request")]
                ]
                country_text = "اختر الدولة:"
            else:
                keyboard = [
                    [InlineKeyboardButton("🇺🇸 United States", callback_data="country_US_verizon")],
                    [InlineKeyboardButton("🔙 Back", callback_data="cancel_user_proxy_request")]
                ]
                country_text = "Choose country:"
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(country_text, reply_markup=reply_markup)
            logger.info(f"=== QUANTITY SELECTION SUCCESS (residential verizon) ===")
            
        elif query.data == "quantity_crocker_static":
            logger.info(f"Processing RESIDENTIAL CROCKER for user {user_id}")
            
            # فحص فوري لحالة الخدمة
            if not db.get_service_status('static', 'monthly_verizon'):
                if language == 'ar':
                    await query.edit_message_text("❌ خدمة ريزيدنتال كروكر غير متاحة حالياً\n\nيرجى اختيار خدمة أخرى أو المحاولة لاحقاً.")
                else:
                    await query.edit_message_text("❌ Residential Crocker service is currently unavailable\n\nPlease choose another service or try again later.")
                return
            
            context.user_data['quantity'] = '5'
            context.user_data['static_type'] = 'residential_crocker'
            # عرض دولة أمريكا
            if language == 'ar':
                keyboard = [
                    [InlineKeyboardButton("🇺🇸 الولايات المتحدة", callback_data="country_US_crocker")],
                    [InlineKeyboardButton("🔙 رجوع", callback_data="cancel_user_proxy_request")]
                ]
                country_text = "اختر الدولة:"
            else:
                keyboard = [
                    [InlineKeyboardButton("🇺🇸 United States", callback_data="country_US_crocker")],
                    [InlineKeyboardButton("🔙 Back", callback_data="cancel_user_proxy_request")]
                ]
                country_text = "Choose country:"
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(country_text, reply_markup=reply_markup)
            logger.info(f"=== QUANTITY SELECTION SUCCESS (residential crocker) ===")
            
        elif query.data == "residential_4_dollar":
            logger.info(f"Processing RESIDENTIAL $4 for user {user_id}")
            
            # عرض خيارين: Crocker و Verizon
            verizon_price = get_current_price('verizon')
            if language == 'ar':
                keyboard = [
                    [InlineKeyboardButton(f"🏠 كروكر ({verizon_price}$)", callback_data="quantity_crocker_static")],
                    [InlineKeyboardButton(f"🏠 ڤيرايزون ({verizon_price}$)", callback_data="quantity_verizon_static")],
                    [InlineKeyboardButton("🔙 رجوع", callback_data="cancel_user_proxy_request")]
                ]
                choice_text = "اختر نوع الريزيدنتال $4:"
            else:
                keyboard = [
                    [InlineKeyboardButton(f"🏠 Crocker ({verizon_price}$)", callback_data="quantity_crocker_static")],
                    [InlineKeyboardButton(f"🏠 Verizon ({verizon_price}$)", callback_data="quantity_verizon_static")],
                    [InlineKeyboardButton("🔙 Back", callback_data="cancel_user_proxy_request")]
                ]
                choice_text = "Choose Residential $4 type:"
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(choice_text, reply_markup=reply_markup)
            logger.info(f"=== RESIDENTIAL $4 MENU SHOWN ===")
            
        elif query.data == "quantity_single_socks":
            logger.info(f"Processing SOCKS PACKAGE 5 for user {user_id}")
            
            # فحص فوري لحالة الخدمة
            if not db.get_service_status('socks', 'package_5'):
                if language == 'ar':
                    await query.edit_message_text("❌ خدمة السوكس باكج 5 غير متاحة حالياً\n\nيرجى اختيار خدمة أخرى أو المحاولة لاحقاً.")
                else:
                    await query.edit_message_text("❌ Socks package 5 service is currently unavailable\n\nPlease choose another service or try again later.")
                return
            
            # الحصول على السعر الفعلي من قاعدة البيانات
            socks_prices = get_socks_prices()
            package5_price = float(socks_prices.get('5proxy', '0.4'))
            
            context.user_data['quantity'] = 1  # باكج واحد يحتوي على 5 بروكسي
            context.user_data['proxy_type'] = 'socks'
            context.user_data['socks_price'] = package5_price
            # الانتقال لاختيار الدولة
            await show_country_selection_for_user(query, context, language)
            logger.info(f"=== QUANTITY SELECTION SUCCESS (socks package 5) ===")
            
        elif query.data == "quantity_package_static":
            logger.info(f"Processing RESIDENTIAL 6$ for user {user_id}")
            
            # فحص فوري لحالة الخدمة
            if not db.get_service_status('static', 'monthly_residential'):
                if language == 'ar':
                    await query.edit_message_text("❌ خدمة ريزيدنتال غير متاحة حالياً\n\n🔧 الآدمن أوقف هذه الخدمة مؤقتاً بسبب:\n• تعطل في السيرفرات\n• نفاد الكمية المتاحة\n\nيرجى اختيار خدمة أخرى أو المحاولة لاحقاً.")
                else:
                    await query.edit_message_text("❌ Residential service is currently unavailable\n\nPlease choose another service or try again later.")
                return
            
            context.user_data['quantity'] = '10'
            context.user_data['static_type'] = 'residential_att'
            # الانتقال لاختيار الدولة
            await show_country_selection_for_user(query, context, language)
            logger.info(f"=== QUANTITY SELECTION SUCCESS (residential 6$) ===")
            
        elif query.data == "quantity_package_socks":
            logger.info(f"Processing SOCKS PACKAGE 10 for user {user_id}")
            
            # فحص فوري لحالة الخدمة
            if not db.get_service_status('socks', 'package_10'):
                if language == 'ar':
                    await query.edit_message_text("❌ خدمة السوكس باكج 10 غير متاحة حالياً\n\nيرجى اختيار خدمة أخرى أو المحاولة لاحقاً.")
                else:
                    await query.edit_message_text("❌ Socks package 10 service is currently unavailable\n\nPlease choose another service or try again later.")
                return
            
            # الحصول على السعر الفعلي من قاعدة البيانات
            socks_prices = get_socks_prices()
            package10_price = float(socks_prices.get('10proxy', '0.7'))
            
            context.user_data['quantity'] = 1  # باكج واحد يحتوي على 10 بروكسي
            context.user_data['proxy_type'] = 'socks'
            context.user_data['socks_price'] = package10_price
            # الانتقال لاختيار الدولة
            await show_country_selection_for_user(query, context, language)
            logger.info(f"=== QUANTITY SELECTION SUCCESS (socks package 10) ===")
            
        elif query.data == "quantity_isp_static":
            logger.info(f"Processing ISP for user {user_id}")
            
            # فحص فوري لحالة الخدمة
            if not db.get_service_status('static', 'isp_att'):
                if language == 'ar':
                    await query.edit_message_text("❌ خدمة ISP غير متاحة حالياً\n\n🔧 الآدمن أوقف هذه الخدمة مؤقتاً بسبب:\n• تعطل في السيرفرات\n• نفاد الكمية المتاحة\n\nيرجى اختيار خدمة أخرى أو المحاولة لاحقاً.")
                else:
                    await query.edit_message_text("❌ ISP service is currently unavailable\n\nPlease choose another service or try again later.")
                return
            
            # إزالة الكمية الثابتة - سيتم سؤال المستخدم عنها لاحقاً
            context.user_data['static_type'] = 'isp'
            # الانتقال لاختيار الدولة
            await show_country_selection_for_user(query, context, language)
            logger.info(f"=== QUANTITY SELECTION SUCCESS (isp) ===")
            
        elif query.data == "datacenter_proxy":
            logger.info(f"Processing datacenter proxy for user {user_id}")
            datacenter_price = get_current_price('datacenter')
            if language == 'ar':
                message = f"""🔧 بروكسي داتا سينتر

📦 باقة 100 بروكسي
📅 شهري
💰 السعر: {datacenter_price}$

📞 للطلب الرجاء التواصل مع الإدارة:
@Static_support"""
            else:
                message = f"""🔧 Datacenter Proxy

📦 Package: 100 proxies
📅 Monthly
💰 Price: {datacenter_price}$

📞 To place an order, please contact administration:
@Static_support"""
            await query.message.reply_text(message)
            return
            
        elif query.data == "static_daily":
            logger.info(f"Processing static daily for user {user_id}")
            if language == 'ar':
                await query.message.reply_text("📅 ستاتيك يومي\n🔄 ستتوفر الخدمة قريباً")
            else:
                await query.message.reply_text("📅 Static Daily\n🔄 Service will be available soon")
            return
            
        elif query.data == "static_weekly":
            logger.info(f"Processing static weekly for user {user_id}")
            if language == 'ar':
                await query.message.reply_text("📅 ستاتيك اسبوعي\n🔄 ستتوفر الخدمة قريباً")
            else:
                await query.message.reply_text("📅 Static Weekly\n🔄 Service will be available soon")
            return
        elif query.data == "verizon_weekly":
            # معالج الستاتيك الأسبوعي الجديد
            logger.info(f"Processing verizon weekly for user {user_id}")
            
            # فحص فوري لحالة الخدمة
            if not db.get_service_status('static', 'weekly_crocker'):
                if language == 'ar':
                    await query.edit_message_text("❌ خدمة الستاتيك الأسبوعي Crocker غير متاحة حالياً\n\nيرجى اختيار خدمة أخرى أو المحاولة لاحقاً.")
                else:
                    await query.edit_message_text("❌ Weekly static Crocker service is currently unavailable\n\nPlease choose another service or try again later.")
                return
            
            context.user_data['proxy_type'] = 'static'
            context.user_data['static_type'] = 'verizon_weekly'
            # إزالة الكمية الثابتة - سيتم سؤال المستخدم عنها لاحقاً
            
            # عرض الدول والولايات للستاتيك الأسبوعي
            if language == 'ar':
                message = "🌍 اختر الدولة المطلوبة:"
                keyboard = [
                    [InlineKeyboardButton("🇺🇸 الولايات المتحدة", callback_data="country_US_weekly")],
                    [InlineKeyboardButton("🔙 رجوع", callback_data="cancel_user_proxy_request")]
                ]
            else:
                message = "🌍 Choose the required country:"
                keyboard = [
                    [InlineKeyboardButton("🇺🇸 United States", callback_data="country_US_weekly")],
                    [InlineKeyboardButton("🔙 Back", callback_data="cancel_user_proxy_request")]
                ]
                
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(message, reply_markup=reply_markup)
            return
        else:
            # معالجة قيمة غير متوقعة
            logger.warning(f"Unknown quantity selection: {query.data} from user {user_id}")
            await query.message.reply_text(
                "⚠️ اختيار غير صالح. يرجى المحاولة مرة أخرى أو استخدام /start",
                reply_markup=ReplyKeyboardRemove()
            )
            # تنظيف البيانات والعودة للقائمة الرئيسية
            context.user_data.clear()
            
    except Exception as e:
        logger.error(f"Error in handle_user_quantity_selection for user {user_id}: {e}")
        
        try:
            await update.callback_query.message.reply_text(
                "⚠️ حدث خطأ في معالجة اختيارك. تم إعادة تعيين حالتك.\n"
                "يرجى استخدام /start لإعادة المحاولة.",
                reply_markup=ReplyKeyboardRemove()
            )
            # تنظيف البيانات المؤقتة
            context.user_data.clear()
        except Exception as recovery_error:
            logger.error(f"Failed to send error message in quantity selection: {recovery_error}")

async def show_country_selection_for_user(query, context: ContextTypes.DEFAULT_TYPE, language: str) -> None:
    """عرض اختيار الدولة للمستخدم مع زر إلغاء"""
    try:
        proxy_type = context.user_data.get('proxy_type')
        static_type = context.user_data.get('static_type', '')
        
        if proxy_type == 'socks':
            countries = SOCKS_COUNTRIES.get(language, SOCKS_COUNTRIES['ar'])
        else:
            # للستاتيك، عرض الدول المحددة فقط (بدون أسعار)
            if static_type == 'isp':
                # ISP: فقط الولايات المتحدة
                countries = {
                    'US': STATIC_COUNTRIES[language]['US']
                }
            else:
                # ريزيدنتال: الدول المدعومة فقط
                countries = STATIC_COUNTRIES.get(language, STATIC_COUNTRIES['ar'])
        
        keyboard = []
        for code, name in countries.items():
            keyboard.append([InlineKeyboardButton(name, callback_data=f"country_{code}")])
        
        keyboard.append([InlineKeyboardButton("🔙 رجوع", callback_data="cancel_user_proxy_request")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            MESSAGES[language]['select_country'],
            reply_markup=reply_markup
        )
        
    except Exception as e:
        logger.error(f"Error in show_country_selection_for_user: {e}")
        
        try:
            # محاولة إرسال رسالة خطأ بسيطة
            await query.message.reply_text(
                "⚠️ حدث خطأ في عرض قائمة الدول. يرجى استخدام /start لإعادة المحاولة.",
                reply_markup=ReplyKeyboardRemove()
            )
        except Exception as recovery_error:
            logger.error(f"Failed to send error message in show_country_selection_for_user: {recovery_error}")


async def handle_cancel_user_proxy_request(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالجة إلغاء طلب البروكسي من قبل المستخدم"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    language = get_user_language(user_id)
    is_admin = context.user_data.get('is_admin', False)
    
    # تنظيف البيانات المؤقتة مع الحفاظ على حالة الأدمن
    clean_user_data_preserve_admin(context)
    
    # رسالة الإلغاء
    if language == 'ar':
        cancel_message = "❌ تم إلغاء طلب البروكسي\n\n🔙 يمكنك البدء من جديد في أي وقت"
    else:
        cancel_message = "❌ Proxy request cancelled\n\n🔙 You can start again anytime"
    
    await query.edit_message_text(cancel_message)
    
    # إعادة الكيبورد المناسب حسب نوع المستخدم
    if is_admin:
        await restore_admin_keyboard(context, user_id, "🔧 لوحة الأدمن جاهزة")
    else:
        # إرسال القائمة الرئيسية للمستخدم العادي (6 أزرار كاملة)
        reply_markup = create_main_user_keyboard(language)
        
        await context.bot.send_message(
            user_id,
            MESSAGES[language]['welcome'],
            reply_markup=reply_markup
        )

async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالجة الاستعلامات المرسلة مع حماية من التوقف"""
    query = update.callback_query
    user_id = update.effective_user.id
    
    # قائمة الأزرار التي تُعالج في ConversationHandlers - يجب تجاهلها هنا
    conversation_only_buttons = [
        'confirm_broadcast', 'cancel_broadcast',
        'cancel_order_inquiry', 'cancel_static_prices', 'cancel_socks_prices',
        'cancel_referral_amount', 'cancel_balance_reset', 'cancel_payment_proof',
        'cancel_proxy_setup', 'cancel_user_lookup', 'cancel_password_change',
        'cancel_custom_message',
        # أزرار معالجة الطلبات
        'payment_success', 'payment_failed', 'cancel_processing',
        'quantity_single', 'quantity_package',
        # أزرار أخرى من ConversationHandlers
        'broadcast_all', 'broadcast_custom',
        # أزرار معالجة البروكسي
        'send_custom_message', 'no_custom_message', 'send_proxy_confirm', 'cancel_proxy_send',
        # أزرار أخرى متنوعة
        'quiet_8_18', 'quiet_22_6', 'quiet_12_14', 'quiet_20_22', 'quiet_24h',
        # أزرار البروكسيات المجانية
        'add_free_proxy', 'delete_free_proxy', 'cancel_add_proxy'
    ]
    
    # إذا كان الزر مُعالج في ConversationHandler، لا تتدخل هنا
    if query.data in conversation_only_buttons:
        return
    
    try:
        # التأكد من إجابة الاستعلام أولاً لتجنب تعليق الأزرار
        if not query.data.startswith("show_more_"):  # استثناء للأزرار التي تعالج الإجابة بنفسها
            await query.answer()
    except Exception as answer_error:
        print(f"⚠️ خطأ في إجابة الاستعلام: {answer_error}")
    
    # فحص حالة الحظر وتتبع النقرات المتكررة
    ban_check_result = await check_user_ban_and_track_clicks(update, context)
    if ban_check_result:
        # المستخدم محظور أو تم تطبيق إجراء - إيقاف المعالجة
        return
    
    try:
        logger.info(f"Processing callback query: {query.data} from user {user_id}")
        
        if query.data.startswith("country_") or query.data.startswith("state_"):
            logger.info(f"Routing to country selection for user {user_id}")
            await handle_country_selection(update, context)
        elif query.data.startswith("payment_"):
            logger.info(f"Routing to payment selection for user {user_id}")
            await handle_payment_method_selection(update, context)
        elif query.data.startswith("recharge_payment_"):
            logger.info(f"Routing to recharge payment selection for user {user_id}")
            await handle_recharge_payment_method_selection(update, context)
        elif query.data.startswith("lang_"):
            logger.info(f"Routing to language change for user {user_id}")
            await handle_language_change(update, context)
        elif query.data.startswith("quantity_") or query.data in ["static_daily", "static_weekly", "verizon_weekly", "datacenter_proxy", "residential_4_dollar"]:
            logger.info(f"Routing to quantity selection: {query.data} for user {user_id}")
            await handle_user_quantity_selection(update, context)
        elif query.data.startswith("view_pending_order_"):
            logger.info(f"Routing to pending order details for user {user_id}")
            await handle_view_pending_order_details(update, context)
        elif query.data.startswith("direct_process_"):
            logger.info(f"Routing to direct order processing for user {user_id}")
            await handle_direct_process_order(update, context)
        elif query.data == "back_to_pending_orders":
            logger.info(f"Routing back to pending orders for user {user_id}")
            await handle_back_to_pending_orders(update, context)
        elif query.data == "admin_main_menu":
            logger.info(f"Routing to admin main menu for user {user_id}")
            await query.answer()
            await restore_admin_keyboard(context, update.effective_chat.id, "🏠 العودة للقائمة الرئيسية")
        elif query.data.startswith("view_order_"):
            logger.info(f"Routing to order details for user {user_id}")
            await handle_view_order_details(update, context)
        elif query.data == "cancel_user_proxy_request":
            await handle_cancel_user_proxy_request(update, context)
        # تم نقل معالجة process_ إلى process_order_conv_handler
        # تم نقل معالجة payment_success و payment_failed إلى process_order_conv_handler
        # تم نقل معالجة proxy_type_ إلى process_order_conv_handler
        # تم نقل معالجة admin_country_ و admin_state_ إلى process_order_conv_handler
        elif query.data in ["admin_referrals", "user_lookup", "manage_money", "admin_settings", "reset_balance"]:
            await handle_admin_menu_actions(update, context)
        elif query.data == "withdraw_balance":
            await handle_withdrawal_request(update, context)
        # approve_recharge_ تم نقلها إلى recharge_approval_conv_handler
        elif query.data.startswith("reject_recharge_"):
            logger.info(f"Routing to recharge rejection for user {user_id}")
            await handle_reject_recharge(update, context)
        elif query.data.startswith("view_recharge_"):
            logger.info(f"Routing to recharge details for user {user_id}")
            await handle_view_recharge_details(update, context)
        elif query.data.startswith("use_admin_amount_") or query.data.startswith("use_user_amount_") or query.data.startswith("stop_processing_"):
            logger.info(f"Routing to recharge amount choice for user {user_id}")
            await handle_recharge_amount_choice(update, context)
        elif query.data in ["confirm_logout", "cancel_logout"]:
            await handle_logout_confirmation(update, context)
        elif query.data == "back_to_admin":
            await handle_back_to_admin(update, context)
        elif query.data == "show_bot_services":
            await handle_show_bot_services(update, context)
        elif query.data == "show_exchange_rate":
            await handle_show_exchange_rate(update, context)
        elif query.data == "send_proxy_confirm":
            thank_message = context.user_data.get('admin_thank_message', '')
            await send_proxy_to_user(update, context, thank_message)
            
            # إنشاء زر "تم إنهاء الطلب بنجاح"
            keyboard = [[InlineKeyboardButton("✅ تم إنهاء الطلب بنجاح", callback_data="order_completed_success")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                "✅ تم إرسال البروكسي للمستخدم بنجاح!",
                reply_markup=reply_markup
            )
        elif query.data == "cancel_proxy_send":
            # إلغاء إرسال البروكسي وتنظيف البيانات
            order_id = context.user_data.get('processing_order_id')
            if order_id:
                # تنظيف البيانات المؤقتة
                admin_keys = [k for k in context.user_data.keys() if k.startswith('admin_')]
                for key in admin_keys:
                    context.user_data.pop(key, None)
                context.user_data.pop('processing_order_id', None)
            
            await query.edit_message_text(
                f"❌ تم إلغاء إرسال البروكسي\n\n🆔 معرف الطلب: {order_id}\n\n📋 الطلب لا يزال في حالة معلق ويمكن معالجته لاحقاً.",
                parse_mode='Markdown'
            )
            
            # إعادة تفعيل كيبورد الأدمن الرئيسي
            await restore_admin_keyboard(context, update.effective_chat.id)
        elif query.data == "order_completed_success":
            # تمت معالجة هذا الزر في ConversationHandler - تجاهل هنا
            await query.answer("تم إنهاء الطلب بنجاح!")
        elif query.data == "developer_info":
            # إظهار نافذة منبثقة مع معلومات المطور
            user_id = update.effective_user.id
            language = get_user_language(user_id)
            
            # إنشاء النص بناءً على لغة المستخدم الحالية (مختصر للنافذة المنبثقة)
            if language == 'ar':
                popup_text = """🧑‍💻 معلومات المطور

📦 بوت بيع البروكسي v1.0.0
👨‍💻 طُور بواسطة: Mohamad Zalaf

📱 تليجرام: @MohamadZalaf
📧 MohamadZalaf@outlook.com

© Mohamad Zalaf 2025"""
            else:
                popup_text = """🧑‍💻 Developer Information

📦 Proxy Sales Bot v1.0.0
👨‍💻 Developed by: Mohamad Zalaf

📱 Telegram: @MohamadZalaf
📧 MohamadZalaf@outlook.com

© Mohamad Zalaf 2025"""
            
            try:
                await query.answer(text=popup_text, show_alert=True)
            except Exception as e:
                logger.error(f"Error showing popup: {e}")
                # محاولة بديلة - إرسال رسالة عادية
                await query.message.reply_text(popup_text)
        elif query.data == "manage_proxies":
            # إدارة البروكسيات للأدمن
            await handle_manage_free_proxies(update, context)
        elif query.data == "separator":
            # معالجة الفاصل - عدم القيام بأي شيء
            await query.answer("━━━━━━━━━━━━━━━━━━━━")
        elif query.data == "free_proxy_trial":
            # طلب بروكسي مجاني للمستخدم
            await handle_free_proxy_trial(update, context)
        elif query.data.startswith("use_free_proxy_") or query.data.startswith("get_free_proxy_"):
            # استخدام بروكسي مجاني محدد
            await handle_use_free_proxy(update, context)
        elif query.data == "back_to_manage_proxies":
            # العودة لقائمة إدارة البروكسيات
            await handle_back_to_manage_proxies(update, context)
        elif query.data == "back_to_admin_menu":
            # العودة لقائمة الأدمن الرئيسية
            await handle_back_to_admin_menu(update, context)
        
        # معالجات إدارة خدمات البروكسي الجديدة
        elif query.data == "manage_services":
            await handle_manage_services(update, context)
        elif query.data == "quick_service_control":
            await handle_quick_service_control(update, context)
        elif query.data == "disable_all_countries":
            await handle_toggle_service(update, context)
        elif query.data == "enable_all_countries":
            await handle_toggle_service(update, context)
        elif query.data == "manage_static_services":
            await handle_manage_static_services(update, context)
        elif query.data == "manage_socks_services":
            await handle_manage_socks_services(update, context)
        elif query.data == "manage_socks_countries":
            await handle_manage_countries(update, context)
        elif query.data == "manage_static_countries":
            await handle_manage_static_countries(update, context)
        elif query.data == "manage_free_proxies_menu":
            await handle_manage_free_proxies_menu(update, context)
        elif query.data == "manage_external_proxies":
            await handle_manage_external_proxies(update, context)
        elif query.data == "advanced_service_management":
            await handle_manage_services(update, context)
        elif query.data == "manage_socks_services":
            await handle_manage_socks_services(update, context)
        elif query.data == "manage_static_services":
            await handle_manage_static_services(update, context)
        elif query.data == "manage_external_proxy":
            await handle_manage_external_proxy(update, context)
        elif query.data.startswith("manage_detailed_static_"):
            await handle_manage_detailed_static(update, context)
        elif query.data == "static_services_report":
            await handle_static_services_report(update, context)
        elif query.data == "manage_static_states":
            await handle_manage_static_states(update, context)
        elif query.data == "manage_us_states":
            await handle_manage_us_states(update, context)
        elif query.data == "manage_static_us_states":
            await handle_manage_static_us_states(update, context)
        elif (query.data.startswith("toggle_all_static_") or 
              query.data.startswith("toggle_static_") or
              query.data.startswith("toggle_all_socks_") or 
              query.data.startswith("toggle_socks_") or
              query.data.startswith("toggle_all_countries_") or
              query.data.startswith("toggle_country_socks_") or
              query.data.startswith("toggle_all_static_countries_") or
              query.data.startswith("toggle_country_static_") or
              query.data.startswith("toggle_all_us_states_") or
              query.data.startswith("toggle_state_socks_") or
              query.data.startswith("toggle_all_static_us_states_") or
              query.data.startswith("toggle_state_static_")):
            await handle_toggle_service(update, context)
            
        elif query.data == "cancel_custom_message":
            # إلغاء إدخال الرسالة المخصصة والعودة لقائمة الأدمن
            clean_user_data_preserve_admin(context)
            await query.edit_message_text("❌ تم إلغاء إدخال الرسالة المخصصة.")
            
            # إعادة تفعيل كيبورد الأدمن الرئيسي
            await restore_admin_keyboard(context, update.effective_chat.id)
            
            return ConversationHandler.END

        elif query.data.startswith("quiet_"):
            await handle_quiet_hours_selection(update, context)
        elif query.data in ["confirm_clear_db", "cancel_clear_db"]:
            await handle_database_clear(update, context)
        elif query.data == "cancel_processing":
            await handle_cancel_processing(update, context)
        
        elif query.data == "cancel_direct_processing":
            await handle_cancel_direct_processing(update, context)
        elif query.data.startswith("withdrawal_success_"):
            await handle_withdrawal_success(update, context)
        elif query.data.startswith("withdrawal_failed_"):
            await handle_withdrawal_failed(update, context)
        elif query.data == "cancel_user_lookup":
            await handle_cancel_user_lookup(update, context)
        elif query.data == "cancel_referral_amount":
            await handle_cancel_referral_amount(update, context)
        elif query.data == "cancel_credit_price":
            await handle_cancel_credit_price(update, context)
        elif query.data == "cancel_order_inquiry":
            await handle_cancel_order_inquiry(update, context)
        elif query.data == "cancel_static_prices":
            await handle_cancel_static_prices(update, context)
        elif query.data == "cancel_socks_prices":
            await handle_cancel_socks_prices(update, context)
        elif query.data == "cancel_balance_reset":
            await handle_cancel_balance_reset(update, context)
        elif query.data == "cancel_payment_proof":
            await handle_cancel_payment_proof(update, context)
        elif query.data == "cancel_proxy_setup":
            await handle_cancel_proxy_setup(update, context)
        elif query.data.startswith("show_more_users_"):
            offset = int(query.data.replace("show_more_users_", ""))
            await query.answer()
            await show_user_statistics(update, context, offset)
        elif query.data.startswith("view_order_"):
            await handle_view_order_details(update, context)
        elif query.data.startswith("send_direct_message_"):
            await handle_send_direct_message(update, context)
        elif query.data == "retry_pending_orders":
            # إعادة محاولة تحميل الطلبات المعلقة
            await query.answer("🔄 جاري إعادة المحاولة...")
            await show_pending_orders_admin(update, context)
        elif query.data == "admin_database_menu":
            # انتقال لقائمة إدارة قاعدة البيانات
            await query.answer()
            await database_management_menu(update, context)
        elif query.data == "validate_database":
            # فحص سلامة قاعدة البيانات
            await query.answer("🔍 جاري فحص قاعدة البيانات...")
            await validate_database_status(update, context)
        elif query.data == "back_to_amount":
            await handle_back_to_amount(update, context)
        elif query.data == "back_to_payment_method":
            await handle_back_to_payment_method(update, context)
        elif query.data == "back_to_main_from_recharge":
            await handle_back_to_main_from_recharge(update, context)
        # معالجة أزرار أسعار السوكس الجديدة
        elif query.data in ["set_socks_single", "set_socks_double", "set_socks_package5", "set_socks_package10", "back_to_prices_menu"]:
            logger.info(f"Routing to SOCKS price handler: {query.data} for user {user_id}")
            await handle_socks_price_callback(update, context)
        # معالجة أزرار إدارة المستخدمين الجديدة
        elif query.data == "back_to_admin_menu":
            await query.answer()
            await restore_admin_keyboard(context, update.effective_chat.id, "🔧 تم العودة لقائمة الأدمن")
        elif query.data.startswith("manage_user_"):
            await handle_manage_user(update, context)
        elif query.data.startswith("manage_points_"):
            await handle_manage_points(update, context)
        elif query.data.startswith("broadcast_user_"):
            await handle_broadcast_user(update, context)
        elif query.data.startswith("manage_referrals_"):
            await handle_manage_referrals(update, context)
        elif query.data.startswith("detailed_reports_"):
            await handle_detailed_reports(update, context)
        # معالجة أحداث إدارة المستخدم المتقدمة
        elif query.data.startswith("ban_user_"):
            await handle_ban_user_action(update, context)
        elif query.data.startswith("unban_user_"):
            await handle_unban_user_action(update, context)
        elif query.data.startswith("remove_temp_ban_"):
            await handle_remove_temp_ban_action(update, context)
        elif query.data.startswith("add_points_"):
            await handle_add_points_action(update, context)
        elif query.data.startswith("subtract_points_"):
            await handle_subtract_points_action(update, context)
        elif query.data.startswith("add_referral_"):
            await handle_add_referral_action(update, context)
        elif query.data.startswith("delete_referral_"):
            await handle_delete_referral_action(update, context)
        elif query.data.startswith("reset_referral_balance_"):
            await handle_reset_referral_balance_action(update, context)
        elif query.data.startswith("send_text_"):
            await handle_single_user_broadcast_action(update, context)
        elif query.data.startswith("send_photo_"):
            await handle_single_user_broadcast_photo_action(update, context)
        elif query.data.startswith("quick_message_"):
            await handle_quick_message_action(update, context)
        elif query.data.startswith("important_notice_"):
            await handle_important_notice_action(update, context)
        elif query.data.startswith("back_to_profile_"):
            await handle_back_to_user_profile(update, context)
        # معالجة أحداث التأكيد الجديدة
        elif query.data.startswith("confirm_ban_"):
            await handle_confirm_ban_user(update, context)
        elif query.data.startswith("confirm_unban_"):
            await handle_confirm_unban_user(update, context)
        elif query.data.startswith("confirm_remove_temp_ban_"):
            await handle_confirm_remove_temp_ban(update, context)
        elif query.data.startswith("confirm_reset_referral_balance_"):
            await handle_confirm_reset_referral_balance(update, context)
        elif query.data.startswith("confirm_delete_referral_"):
            await handle_confirm_delete_referral(update, context)
        elif query.data.startswith("quick_template_"):
            await handle_quick_template_selection(update, context)
        # معالجة أزرار التقارير المتقدمة
        elif query.data.startswith("show_referred_"):
            await handle_show_referred_action(update, context)
        elif query.data.startswith("referral_earnings_"):
            await handle_referral_earnings_action(update, context)
        elif query.data.startswith("full_report_"):
            await handle_full_report_action(update, context)
        elif query.data.startswith("financial_report_"):
            await handle_financial_report_action(update, context)
        elif query.data.startswith("orders_report_"):
            await handle_orders_report_action(update, context)
        elif query.data.startswith("referrals_report_"):
            await handle_referrals_report_action(update, context)
        elif query.data.startswith("advanced_stats_"):
            await handle_advanced_stats_action(update, context)
        elif query.data.startswith("timeline_report_"):
            await handle_timeline_report_action(update, context)
        elif query.data.startswith("transaction_history_"):
            await handle_transaction_history_action(update, context)
        elif query.data.startswith("custom_balance_"):
            await handle_custom_balance_action(update, context)
        elif query.data.startswith("reset_stats_"):
            await handle_reset_stats_action(update, context)
        elif query.data.startswith("delete_user_data_"):
            await handle_delete_user_data_action(update, context)
        elif query.data.startswith("clear_referrals_"):
            await handle_clear_referrals_action(update, context)
        else:
            # معالجة الأزرار غير المعروفة أو المنتهية الصلاحية
            logger.warning(f"Unknown or expired callback action: {query.data} from user {user_id}")
            
            try:
                await query.answer("⚠️ هذا الزر منتهي الصلاحية أو غير صالح")
            except Exception as answer_error:
                logger.error(f"Failed to answer unknown callback: {answer_error}")
            
            # تنظيف البيانات المؤقتة لتجنب التعليق
            context.user_data.clear()
            
            # التحقق من نوع المستخدم وإعادة توجيهه للقائمة المناسبة
            if user_id in ACTIVE_ADMINS or context.user_data.get('is_admin'):
                # للأدمن - إعادة تفعيل كيبورد الأدمن
                await restore_admin_keyboard(context, update.effective_chat.id, 
                                           "⚠️ تم اكتشاف زر منتهي الصلاحية. عودة للقائمة الرئيسية...")
            else:
                # للمستخدم العادي - العودة للقائمة الرئيسية
                try:
                    await query.message.reply_text(
                        "⚠️ هذا الزر منتهي الصلاحية. تم إعادة توجيهك للقائمة الرئيسية.",
                        reply_markup=ReplyKeyboardRemove()
                    )
                    await start(update, context)
                except Exception as redirect_error:
                    logger.error(f"Failed to redirect user after unknown callback: {redirect_error}")
                    # محاولة أخيرة بسيطة
                    try:
                        await context.bot.send_message(
                            user_id,
                            "يرجى استخدام /start لإعادة تشغيل البوت"
                        )
                    except:
                        pass
            
    except Exception as e:
        logger.error(f"Error in handle_callback_query from user {update.effective_user.id}: {e}")
        print(f"❌ خطأ في معالجة callback query من المستخدم {update.effective_user.id}: {e}")
        print(f"   البيانات: {query.data}")
        
        # محاولة إجابة الاستعلام لتجنب تعليق الأزرار
        try:
            await query.answer("❌ حدث خطأ، جاري إعادة التوجيه...")
        except:
            pass
        
        # إعادة توجيه المستخدم مع تفاصيل الخطأ للآدمن
        try:
            user_id = update.effective_user.id
            if context.user_data.get('is_admin') or user_id in ACTIVE_ADMINS:
                error_details = f"❌ حدث خطأ في معالجة العملية\n\n🔍 التفاصيل التقنية:\n• نوع العملية: {query.data}\n• سبب الخطأ: {str(e)[:200]}...\n\n🔧 تم إعادة توجيهك للقائمة الرئيسية"
                await restore_admin_keyboard(context, update.effective_chat.id, error_details)
            else:
                await start(update, context)
        except Exception as redirect_error:
            logger.error(f"Failed to redirect after callback error: {redirect_error}")
            print(f"❌ فشل في إعادة التوجيه: {redirect_error}")
        
        # تنظيف البيانات المؤقتة في حالة الخطأ
        try:
            clean_user_data_preserve_admin(context)
        except:
            pass

async def handle_admin_country_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """معالجة اختيار الدولة من قبل الأدمن"""
    query = update.callback_query
    await query.answer()
    
    # معالجة التنقل بين الصفحات
    if query.data.startswith("admin_country_page_"):
        page = int(query.data.replace("admin_country_page_", ""))
        proxy_type = context.user_data.get('admin_proxy_type', 'static')
        countries = SOCKS_COUNTRIES['ar'] if proxy_type == 'socks' else STATIC_COUNTRIES['ar']
        
        reply_markup = create_paginated_keyboard(countries, "admin_country_", page, 8, 'ar')
        await query.edit_message_text("4️⃣ اختر الدولة:", reply_markup=reply_markup)
        return ENTER_COUNTRY
    
    # معالجة التنقل بين صفحات الولايات
    elif query.data.startswith("admin_state_page_"):
        page = int(query.data.replace("admin_state_page_", ""))
        country_code = context.user_data.get('current_country_code', '')
        # لدالة الأدمن، نستخدم المعايير الافتراضية
        proxy_type = context.user_data.get('admin_proxy_type', 'static')
        states = get_states_for_country(country_code, proxy_type, 'residential')
        
        if states:
            reply_markup = create_paginated_keyboard(states['ar'], "admin_state_", page, 8, 'ar')
            await query.edit_message_text("5️⃣ اختر الولاية:", reply_markup=reply_markup)
        return ENTER_STATE
    
    elif query.data == "admin_country_other":
        context.user_data['admin_input_state'] = ENTER_COUNTRY
        await query.edit_message_text("4️⃣ يرجى إدخال اسم الدولة:")
        return ENTER_COUNTRY
    
    elif query.data.startswith("admin_state_"):
        if query.data == "admin_state_other":
            context.user_data['admin_input_state'] = ENTER_STATE
            await query.edit_message_text("5️⃣ يرجى إدخال اسم الولاية:")
            return ENTER_STATE
        else:
            state_code = query.data.replace("admin_state_", "")
            country_code = context.user_data.get('current_country_code', '')
            proxy_type = context.user_data.get('admin_proxy_type', 'static')
            states = get_states_for_country(country_code, proxy_type, 'residential')
            
            if states:
                context.user_data['admin_proxy_state'] = states['ar'].get(state_code, state_code)
            else:
                context.user_data['admin_proxy_state'] = state_code
                
            context.user_data['admin_input_state'] = ENTER_USERNAME
            await query.edit_message_text("6️⃣ يرجى إدخال اسم المستخدم للبروكسي:")
            return ENTER_USERNAME
    
    else:
        country_code = query.data.replace("admin_country_", "")
        context.user_data['current_country_code'] = country_code
        
        # تحديد قائمة الدول المناسبة
        proxy_type = context.user_data.get('admin_proxy_type', 'static')
        if proxy_type == 'socks':
            context.user_data['admin_proxy_country'] = SOCKS_COUNTRIES['ar'].get(country_code, country_code)
        else:
            context.user_data['admin_proxy_country'] = STATIC_COUNTRIES['ar'].get(country_code, country_code)
        
        # عرض قائمة الولايات إذا كانت متوفرة
        proxy_type = context.user_data.get('admin_proxy_type', 'static')
        states = get_states_for_country(country_code, proxy_type, 'residential')
        
        if states:
            reply_markup = create_paginated_keyboard(states['ar'], "admin_state_", 0, 8, 'ar')
            await query.edit_message_text("5️⃣ اختر الولاية:", reply_markup=reply_markup)
            return ENTER_STATE
        else:
            # انتقل مباشرة لاسم المستخدم
            context.user_data['admin_input_state'] = ENTER_USERNAME
            await query.edit_message_text("6️⃣ يرجى إدخال اسم المستخدم للبروكسي:")
            return ENTER_USERNAME

async def handle_withdrawal_request(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالجة طلب سحب الرصيد"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    user = db.get_user(user_id)
    language = get_user_language(user_id)
    
    if user and float(user[5]) >= 1.0:  # الحد الأدنى 1 دولار
        # إنشاء معرف طلب السحب
        withdrawal_id = generate_order_id()
        
        # حفظ طلب السحب في قاعدة البيانات
        db.execute_query(
            "INSERT INTO orders (id, user_id, proxy_type, payment_amount, status) VALUES (?, ?, ?, ?, ?)",
            (withdrawal_id, user_id, 'withdrawal', user[5], 'pending')
        )
        
        if language == 'ar':
            message = f"""💸 تم إرسال طلب سحب الرصيد

💰 المبلغ المطلوب: `{user[5]:.2f}$`
🆔 معرف الطلب: `{withdrawal_id}`

تم إرسال طلبك للأدمن وسيتم معالجته في أقرب وقت ممكن."""
        else:
            message = f"""💸 Withdrawal request sent

💰 Amount: `{user[5]:.2f}$`
🆔 Request ID: `{withdrawal_id}`

Your request has been sent to admin and will be processed soon."""
        
        # إرسال إشعار طلب السحب للأدمن
        await send_withdrawal_notification(context, withdrawal_id, user)
        
        await query.edit_message_text(message, parse_mode='Markdown')
    else:
        min_amount = 1.0
        current_balance = float(user[5]) if user else 0.0
        
        if language == 'ar':
            message = f"""❌ رصيد غير كافٍ للسحب

💰 رصيدك الحالي: `{current_balance:.2f}$`
📊 الحد الأدنى للسحب: `{min_amount:.1f}$`

يرجى دعوة المزيد من الأصدقاء لزيادة رصيدك!"""
        else:
            message = f"""❌ Insufficient balance for withdrawal

💰 Current balance: `{current_balance:.2f}$`
📊 Minimum withdrawal: `{min_amount:.1f}$`

Please invite more friends to increase your balance!"""
        
        await query.edit_message_text(message, parse_mode='Markdown')

async def handle_custom_message_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """معالجة اختيار إرسال رسالة مخصصة"""
    query = update.callback_query
    await query.answer()
    
    order_id = context.user_data['processing_order_id']
    
    # التحقق من نوع الطلب (فشل أو نجاح)
    if query.data == "send_custom_message_failed":
        # تدفق الفشل - إرسال رسالة مخصصة بعد الرفض
        keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data="cancel_custom_message")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("يرجى إدخال الرسالة المخصصة للمستخدم:", reply_markup=reply_markup)
        return CUSTOM_MESSAGE
        
    elif query.data == "no_custom_message_failed":
        # تدفق الفشل - عدم إرسال رسالة مخصصة
        # تنظيف البيانات المؤقتة
        context.user_data.pop('processing_order_id', None)
        context.user_data.pop('admin_processing_active', None)
        context.user_data.pop('waiting_for_admin_message', None)
        context.user_data.pop('direct_processing', None)
        context.user_data.pop('custom_mode', None)
        
        await query.edit_message_text(f"✅ تم رفض الطلب وإشعار المستخدم.\nمعرف الطلب: {order_id}")
        
        # إعادة تفعيل كيبورد الأدمن الرئيسي
        await restore_admin_keyboard(context, update.effective_chat.id)
        
        return ConversationHandler.END
    
    elif query.data == "send_custom_message":
        # كود قديم للتوافق (إذا كان موجوداً)
        keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data="cancel_custom_message")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("يرجى إدخال الرسالة المخصصة للمستخدم:", reply_markup=reply_markup)
        return CUSTOM_MESSAGE
    else:
        # عدم إرسال رسالة مخصصة
        user_query = "SELECT user_id FROM orders WHERE id = ?"
        user_result = db.execute_query(user_query, (order_id,))
        
        if user_result:
            user_id = user_result[0][0]
            user_language = get_user_language(user_id)
            
            # إرسال رسالة فشل العملية مع معلومات الدعم
            failure_message = {
                'ar': f"""❌ تم رفض طلبك رقم `{order_id}`

إن كان لديك استفسار، يرجى التواصل مع الدعم:
@Static_support""",
                'en': f"""❌ Your order `{order_id}` has been rejected

If you have any questions, please contact support:
@Static_support"""
            }
            
            await context.bot.send_message(
                user_id,
                failure_message[user_language],
                parse_mode='Markdown'
            )
        
        # جدولة حذف الطلب بعد 48 ساعة
        await schedule_order_deletion(context, order_id, user_id if user_result else None)
        
        # تنظيف البيانات المؤقتة مع الحفاظ على حالة الأدمن
        clean_user_data_preserve_admin(context)
        
        await query.edit_message_text(f"✅ تم إشعار المستخدم برفض الطلب.\nمعرف الطلب: {order_id}\n\n⏰ سيتم حذف الطلب تلقائياً بعد 48 ساعة")
        
        # إعادة تفعيل كيبورد الأدمن الرئيسي
        await restore_admin_keyboard(context, update.effective_chat.id)
        
        return ConversationHandler.END

async def handle_custom_message_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """معالجة إدخال الرسالة المخصصة"""
    custom_message = update.message.text
    order_id = context.user_data.get('processing_order_id')
    
    if not order_id:
        await update.message.reply_text("❌ حدث خطأ في معرف الطلب")
        await restore_admin_keyboard(context, update.effective_chat.id)
        return ConversationHandler.END
    
    # حارس لمنع التداخل: التحقق من وضع الرسالة المخصصة
    custom_mode = context.user_data.get('custom_mode', 'success')
    
    # إذا كان الوضع "فشل" - معالجة رسالة مخصصة بعد الرفض
    if custom_mode == 'failed':
        # تدفق الفشل: إرسال الرسالة المخصصة فقط بدون خصم رصيد أو إتمام طلب
        user_query = "SELECT user_id FROM orders WHERE id = ?"
        user_result = db.execute_query(user_query, (order_id,))
        
        if user_result:
            user_id = user_result[0][0]
            
            # إرسال الرسالة المخصصة للمستخدم فقط
            admin_message_template = f"""📩 لديك رسالة من الأدمن

"{custom_message}"

━━━━━━━━━━━━━━━━━"""
            
            await context.bot.send_message(user_id, admin_message_template)
        
        # تنظيف البيانات المؤقتة
        context.user_data.pop('processing_order_id', None)
        context.user_data.pop('admin_processing_active', None)
        context.user_data.pop('waiting_for_admin_message', None)
        context.user_data.pop('direct_processing', None)
        context.user_data.pop('custom_mode', None)
        
        await update.message.reply_text(
            f"✅ تم إرسال الرسالة المخصصة للمستخدم.\nمعرف الطلب: {order_id}"
        )
        
        # إعادة تفعيل كيبورد الأدمن الرئيسي
        await restore_admin_keyboard(context, update.effective_chat.id)
        return ConversationHandler.END
    
    # تدفق النجاح: معالجة عادية
    # التحقق من أن هذا تدفق البروكسي الجديد (مباشرة بدون أزرار الكمية)
    if context.user_data.get('waiting_for_admin_message', False):
        # التدفق الجديد: إرسال البروكسي مع الرسالة المخصصة
        await send_proxy_with_custom_message(update, context, custom_message)
        return ConversationHandler.END
    else:
        # التدفق القديم: إرسال رسالة فشل
        user_query = "SELECT user_id FROM orders WHERE id = ?"
        user_result = db.execute_query(user_query, (order_id,))
        
        if user_result:
            user_id = user_result[0][0]
            user_language = get_user_language(user_id)
            
            # إرسال الرسالة المخصصة في قالب جاهز
            admin_message_template = f"""📩 لديك رسالة من الأدمن

"{custom_message}"

━━━━━━━━━━━━━━━━━"""
            
            await context.bot.send_message(user_id, admin_message_template)
            
            # إرسال رسالة فشل العملية
            failure_message = {
                'ar': f"""❌ تم رفض طلبك رقم `{order_id}`

إن كان لديك استفسار، يرجى التواصل مع الدعم:
@Static_support""",
                'en': f"""❌ Your order `{order_id}` has been rejected

If you have any questions, please contact support:
@Static_support"""
            }
            
            await context.bot.send_message(
                user_id,
                failure_message[user_language],
                parse_mode='Markdown'
            )
            
            # جدولة حذف الطلب بعد 48 ساعة
            await schedule_order_deletion(context, order_id, user_id)
        
        # تنظيف البيانات المؤقتة مع الحفاظ على حالة الأدمن
        clean_user_data_preserve_admin(context)
        
        await update.message.reply_text(
            f"✅ تم إرسال الرسالة المخصصة ورسالة فشل العملية للمستخدم.\nمعرف الطلب: {order_id}\n\n⏰ سيتم حذف الطلب تلقائياً بعد 48 ساعة"
        )
        
        # إعادة تفعيل كيبورد الأدمن الرئيسي
        await restore_admin_keyboard(context, update.effective_chat.id)
        return ConversationHandler.END

async def send_proxy_with_custom_message(update: Update, context: ContextTypes.DEFAULT_TYPE, custom_message: str) -> None:
    """إرسال البروكسي مع الرسالة المخصصة مباشرة"""
    order_id = context.user_data['processing_order_id']
    
    # الحصول على معلومات المستخدم والطلب
    user_query = """
        SELECT o.user_id, u.first_name, u.last_name 
        FROM orders o 
        JOIN users u ON o.user_id = u.user_id 
        WHERE o.id = ?
    """
    user_result = db.execute_query(user_query, (order_id,))
    
    if user_result:
        user_id, first_name, last_name = user_result[0]
        user_full_name = f"{first_name} {last_name or ''}".strip()
        
        # معلومات البروكسي ستأتي من رسالة الأدمن المخصصة
        
        # الحصول على التاريخ والوقت الحاليين
        from datetime import datetime
        now = datetime.now()
        current_date = now.strftime("%Y-%m-%d")
        current_time = now.strftime("%H:%M:%S")
        
        # الحصول على لغة المستخدم وإنشاء رسالة البروكسي
        user_language = get_user_language(user_id)
        
        if user_language == 'ar':
            proxy_message = f"""✅ تم معالجة طلب {user_full_name}

🔐 تفاصيل البروكسي:
{custom_message}

━━━━━━━━━━━━━━━
🆔 معرف الطلب: {order_id}
📅 التاريخ: {current_date}
🕐 الوقت: {current_time}

━━━━━━━━━━━━━━━
✅ تم إنجاز طلبك بنجاح!"""
        else:
            proxy_message = f"""✅ Order processed for {user_full_name}

🔐 Proxy Details:
{custom_message}

━━━━━━━━━━━━━━━
🆔 Order ID: {order_id}
📅 Date: {current_date}
🕐 Time: {current_time}

━━━━━━━━━━━━━━━
✅ Your order has been completed successfully!"""
        
        # اقتطاع الرصيد من المستخدم عند إرسال البروكسي (هذا هو التوقيت الصحيح)
        order_query = "SELECT user_id, payment_amount, proxy_type FROM orders WHERE id = ?"
        order_result = db.execute_query(order_query, (order_id,))
        
        if order_result:
            order_user_id, payment_amount, proxy_type = order_result[0]
            
            # اقتطاع الرصيد (مع السماح بالرصيد السالب لمنع التحايل)
            try:
                db.deduct_credits(
                    order_user_id, 
                    payment_amount, 
                    'proxy_purchase', 
                    order_id, 
                    f"شراء بروكسي {proxy_type}",
                    allow_negative=True  # السماح بالرصيد السالب
                )
                logger.info(f"تم اقتطاع {payment_amount} نقطة من المستخدم {order_user_id} للطلب {order_id}")
            except Exception as deduct_error:
                logger.error(f"Error deducting points for order {order_id}: {deduct_error}")
        
        # إرسال البروكسي للمستخدم
        await context.bot.send_message(user_id, proxy_message, parse_mode='Markdown')
        
        # تحديث حالة الطلب
        proxy_details = {
            'admin_message': custom_message,
            'processed_date': current_date,
            'processed_time': current_time
        }
        
        # تسجيل الطلب كمكتمل ومعالج فعلياً
        db.execute_query(
            "UPDATE orders SET status = 'completed', processed_at = CURRENT_TIMESTAMP, proxy_details = ?, truly_processed = TRUE WHERE id = ?",
            (json.dumps(proxy_details), order_id)
        )
        
        # التحقق من إضافة رصيد الإحالة لأول عملية شراء
        await check_and_add_referral_bonus(context, user_id, order_id)
        
        # رسالة تأكيد للأدمن
        admin_message = f"""✅ تم معالجة الطلب وإرسال البروكسي بنجاح!

🆔 معرف الطلب: {order_id}
👤 المستخدم: {user_full_name}

🔐 تفاصيل البروكسي المرسلة:
{custom_message}

━━━━━━━━━━━━━━━
✅ تم إنهاء معالجة الطلب بنجاح"""

        await update.message.reply_text(admin_message, parse_mode='Markdown')
        
        # تنظيف البيانات المؤقتة
        clean_user_data_preserve_admin(context)
        
        # إعادة تفعيل كيبورد الأدمن الرئيسي
        await restore_admin_keyboard(context, update.effective_chat.id)

async def handle_admin_message_for_proxy(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """معالجة رسالة الأدمن التي تحتوي على معلومات البروكسي"""
    # التحقق من أن هناك طلب قيد المعالجة وانتظار رسالة
    if not context.user_data.get('processing_order_id') or not context.user_data.get('waiting_for_admin_message'):
        # في حالة فقدان السياق، محاولة الحصول على معرف الطلب من custom message input
        if context.user_data.get('processing_order_id'):
            custom_message = update.message.text
            await send_proxy_with_custom_message(update, context, custom_message)
            return ConversationHandler.END
        else:
            await update.message.reply_text("❌ لا يوجد طلب قيد المعالجة حالياً")
            await restore_admin_keyboard(context, update.effective_chat.id)
            return ConversationHandler.END
    
    custom_message = update.message.text
    order_id = context.user_data['processing_order_id']
    
    try:
        # استدعاء دالة إرسال البروكسي مع الرسالة المخصصة
        await send_proxy_with_custom_message(update, context, custom_message)
        
        # رسالة تأكيد للأدمن
        await update.message.reply_text(
            f"✅ تم إرسال البروكسي والرسالة للمستخدم بنجاح!\n\n🆔 معرف الطلب: {order_id}",
            parse_mode='Markdown'
        )
        
        # إعادة تفعيل كيبورد الأدمن
        await restore_admin_keyboard(context, update.effective_chat.id)
        
        return ConversationHandler.END
        
    except Exception as e:
        logger.error(f"خطأ في إرسال البروكسي: {e}")
        await update.message.reply_text(
            f"❌ حدث خطأ أثناء إرسال البروكسي\n\nالخطأ: {str(e)}"
        )
        return PROCESS_ORDER

async def schedule_order_deletion(context: ContextTypes.DEFAULT_TYPE, order_id: str, user_id: int = None) -> None:
    """جدولة حذف الطلب بعد 48 ساعة"""
    import asyncio
    
    async def delete_after_48_hours():
        # انتظار 48 ساعة (48 * 60 * 60 ثانية)
        await asyncio.sleep(48 * 60 * 60)
        
        try:
            # حذف الطلب من قاعدة البيانات
            db.execute_query("DELETE FROM orders WHERE id = ? AND status = 'failed'", (order_id,))
            
            # إشعار المستخدم بانتهاء صلاحية الطلب
            if user_id:
                user_language = get_user_language(user_id)
                failure_message = {
                    'ar': f"⏰ انتهت صلاحية الطلب `{order_id}` وتم حذفه من النظام.\n\n💡 يمكنك إنشاء طلب جديد في أي وقت.",
                    'en': f"⏰ Order `{order_id}` has expired and been deleted from the system.\n\n💡 You can create a new order anytime."
                }
                
                await context.bot.send_message(
                    user_id,
                    failure_message[user_language],
                    parse_mode='Markdown'
                )
        except Exception as e:
            logger.error(f"Error deleting expired order {order_id}: {e}")
    
    # تشغيل المهمة في الخلفية
    context.application.create_task(delete_after_48_hours())

# إضافة المزيد من الوظائف المساعدة
async def add_referral_bonus(user_id: int, referred_user_id: int) -> None:
    """إضافة مكافأة الإحالة"""
    # الحصول على قيمة الإحالة من الإعدادات
    referral_amount_query = "SELECT value FROM settings WHERE key = 'referral_amount'"
    result = db.execute_query(referral_amount_query)
    referral_amount = float(result[0][0]) if result else 0.1
    
    # إضافة الإحالة
    db.execute_query(
        "INSERT INTO referrals (referrer_id, referred_id, amount) VALUES (?, ?, ?)",
        (user_id, referred_user_id, referral_amount)
    )

async def activate_referral_bonus_on_success(context, user_id: int) -> None:
    """تفعيل مكافأة الإحالة عند أول عملية شراء ناجحة"""
    # البحث عن إحالة غير مفعلة لهذا المستخدم
    query = """
        SELECT r.id, r.referrer_id, r.amount 
        FROM referrals r
        WHERE r.referred_id = ? 
        AND NOT EXISTS (
            SELECT 1 FROM orders o 
            WHERE o.user_id = r.referred_id 
            AND o.status = 'completed' 
            AND o.truly_processed = TRUE 
            AND o.created_at < (SELECT created_at FROM orders WHERE user_id = ? AND status = 'completed' AND truly_processed = TRUE ORDER BY created_at DESC LIMIT 1)
        )
        LIMIT 1
    """
    result = db.execute_query(query, (user_id, user_id))
    
    if result:
        referral_id, referrer_id, amount = result[0]
        
        # إضافة الرصيد للمحيل
        db.execute_query(
    #             "UPDATE users SET referral_balance = referral_balance + ? WHERE user_id = ?",
            (amount, referrer_id)
        )
        
        # إشعار المحيل
        try:
            await context.bot.send_message(
                referrer_id,
                parse_mode='Markdown'
            )
        except:
            pass

    
    # تأجيل إضافة الرصيد حتى أول عملية شراء ناجحة
    db.execute_query(
    #         "UPDATE users SET referral_balance = referral_balance + ? WHERE user_id = ?",
    #         (referral_amount, user_id)
    )

async def cleanup_old_orders() -> None:
    """تنظيف الطلبات القديمة (48 ساعة)"""
    # حذف الطلبات الفاشلة القديمة (بعد 48 ساعة كما هو مطلوب في المواصفات)
    deleted_failed = db.execute_query("""
        DELETE FROM orders 
        WHERE status = 'failed' 
        AND created_at < datetime('now', '-48 hours')
    """)
    
    # تسجيل عدد الطلبات المحذوفة
    if deleted_failed:
        print(f"تم حذف {len(deleted_failed)} طلب فاشل قديم")
    
    # يمكن الاحتفاظ بالطلبات المكتملة للإحصائيات (لا نحذفها)



def create_requirements_file():
    """إنشاء ملف requirements.txt"""
    requirements = """python-telegram-bot==20.7
pandas>=1.3.0
openpyxl>=3.0.0"""
    
    with open("requirements.txt", "w", encoding="utf-8") as f:
        f.write(requirements)

async def export_database_excel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """تصدير قاعدة البيانات إلى Excel"""
    try:
        # قراءة البيانات من قاعدة البيانات
        conn = sqlite3.connect(DATABASE_FILE)
        
        # إنشاء ملف Excel مع عدة أوراق
        with pd.ExcelWriter('database_export.xlsx', engine='openpyxl') as writer:
            # جدول المستخدمين
            users_df = pd.read_sql_query("SELECT * FROM users", conn)
            users_df.to_excel(writer, sheet_name='Users', index=False)
            
            # جدول الطلبات
            orders_df = pd.read_sql_query("SELECT * FROM orders", conn)
            orders_df.to_excel(writer, sheet_name='Orders', index=False)
            
            # جدول الإحالات
            referrals_df = pd.read_sql_query("SELECT * FROM referrals", conn)
            referrals_df.to_excel(writer, sheet_name='Referrals', index=False)
            
            # جدول السجلات
            logs_df = pd.read_sql_query("SELECT * FROM logs", conn)
            logs_df.to_excel(writer, sheet_name='Logs', index=False)
        
        conn.close()
        
        # إرسال الملف
        with open('database_export.xlsx', 'rb') as file:
            await update.message.reply_document(
                document=file,
                filename=f"database_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                caption="📊 تم تصدير قاعدة البيانات بصيغة Excel"
            )
        
        # حذف الملف المؤقت
        os.remove('database_export.xlsx')
        
    except Exception as e:
        await update.message.reply_text(f"❌ خطأ في تصدير Excel: {str(e)}")

async def export_database_csv(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """تصدير قاعدة البيانات إلى CSV"""
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        
        # تصدير جدول المستخدمين
        users_df = pd.read_sql_query("SELECT * FROM users", conn)
        users_df.to_csv('users_export.csv', index=False, encoding='utf-8-sig')
        
        # تصدير جدول الطلبات
        orders_df = pd.read_sql_query("SELECT * FROM orders", conn)
        orders_df.to_csv('orders_export.csv', index=False, encoding='utf-8-sig')
        
        conn.close()
        
        # إرسال الملفات
        with open('users_export.csv', 'rb') as file:
            await update.message.reply_document(
                document=file,
                filename=f"users_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                caption="👥 بيانات المستخدمين - CSV"
            )
        
        with open('orders_export.csv', 'rb') as file:
            await update.message.reply_document(
                document=file,
                filename=f"orders_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                caption="📋 بيانات الطلبات - CSV"
            )
        
        # حذف الملفات المؤقتة
        os.remove('users_export.csv')
        os.remove('orders_export.csv')
        
    except Exception as e:
        await update.message.reply_text(f"❌ خطأ في تصدير CSV: {str(e)}")

async def export_database_sqlite(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """تصدير ملف قاعدة البيانات الأصلي"""
    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f"proxy_bot_backup_{timestamp}.db"
        
        # نسخ ملف قاعدة البيانات
        import shutil
        shutil.copy2(DATABASE_FILE, backup_filename)
        
        # إرسال الملف
        with open(backup_filename, 'rb') as file:
            await update.message.reply_document(
                document=file,
                filename=backup_filename,
                caption="🗃️ نسخة احتياطية من قاعدة البيانات - SQLite"
            )
        
        # حذف الملف المؤقت
        os.remove(backup_filename)
        
    except Exception as e:
        await update.message.reply_text(f"❌ خطأ في تصدير قاعدة البيانات: {str(e)}")

async def export_database_json_mix(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """تصدير قاعدة البيانات إلى JSON مع لاحقة .mix"""
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        
        # قراءة جميع الجداول وتحويلها إلى JSON
        database_data = {}
        
        # جدول المستخدمين
        users_df = pd.read_sql_query("SELECT * FROM users", conn)
        database_data['users'] = users_df.to_dict('records')
        
        # جدول الطلبات
        orders_df = pd.read_sql_query("SELECT * FROM orders", conn)
        database_data['orders'] = orders_df.to_dict('records')
        
        # جدول الإحالات
        referrals_df = pd.read_sql_query("SELECT * FROM referrals", conn)
        database_data['referrals'] = referrals_df.to_dict('records')
        
        # جدول السجلات
        logs_df = pd.read_sql_query("SELECT * FROM logs", conn)
        database_data['logs'] = logs_df.to_dict('records')
        
        conn.close()
        
        # إنشاء اسم الملف بلاحقة .mix
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"database_export_{timestamp}.mix"
        
        # كتابة البيانات إلى ملف JSON
        with open(filename, 'w', encoding='utf-8') as file:
            json.dump(database_data, file, ensure_ascii=False, indent=2, default=str)
        
        # إرسال الملف
        with open(filename, 'rb') as file:
            await update.message.reply_document(
                document=file,
                filename=filename,
                caption="🔧 تم التصدير بصيغة mix"
            )
        
        # حذف الملف المؤقت
        os.remove(filename)
        
    except Exception as e:
        await update.message.reply_text(f"❌ خطأ في تصدير JSON: {str(e)}")

def create_readme_file():
    """إنشاء ملف README.md"""
    readme_content = """# بوت بيع البروكسيات - Proxy Sales Bot

## تثبيت المتطلبات

```bash
pip install -r requirements.txt
```

## إعداد البوت

1. احصل على TOKEN من BotFather على تيليجرام
2. ضع التوكن في متغير TOKEN في الكود
3. قم بتشغيل البوت:

```bash
python simpl_bot.py
```

## الميزات

- طلب البروكسيات (Static/Socks)
- نظام دفع متعدد الطرق
- إدارة أدمن متكاملة
- نظام إحالات
- دعم اللغتين العربية والإنجليزية
- قاعدة بيانات SQLite محلية

## أوامر الأدمن

- `/admin_login` - تسجيل دخول الأدمن
- كلمة المرور: `sohilSOHIL`

## البنية

- `simpl_bot.py` - الملف الرئيسي للبوت
- `proxy_bot.db` - قاعدة البيانات (تُنشأ تلقائياً)
- `requirements.txt` - متطلبات Python
"""
    
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(readme_content)

async def handle_process_order(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """معالجة الطلب من قبل الأدمن"""
    query = update.callback_query
    await query.answer()
    
    # التحقق من وجود طلب قيد المعالجة (إنهاء الطلب السابق تلقائياً)
    current_processing_order = context.user_data.get('processing_order_id')
    if current_processing_order:
        # تنظيف الطلب السابق تلقائياً
        try:
            # إعادة الطلب السابق إلى حالة pending إذا لم يكتمل
            db.execute_query(
                "UPDATE orders SET status = 'pending' WHERE id = ? AND status != 'completed'",
                (current_processing_order,)
            )
            
            # تنظيف البيانات المؤقتة للطلب السابق
            context.user_data.pop('waiting_for_direct_admin_message', None)
            context.user_data.pop('waiting_for_admin_message', None)
            context.user_data.pop('direct_processing', None)
            
            await query.answer(f"تم إنهاء الطلب السابق {current_processing_order[:8]}... تلقائياً", show_alert=False)
        except Exception as e:
            print(f"خطأ في تنظيف الطلب السابق: {e}")
    
    order_id = query.data.replace("process_", "")
    
    # تسجيل بداية معالجة طلب جديد
    context.user_data['processing_order_id'] = order_id
    context.user_data['admin_processing_active'] = True
    
    keyboard = [
        [InlineKeyboardButton("نعم", callback_data="payment_success")],
        [InlineKeyboardButton("رفض", callback_data="payment_failed")],
        [InlineKeyboardButton("🔙 رجوع", callback_data="cancel_processing")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # حفظ الرسالة الأصلية قبل التعديل
    context.user_data['original_order_message'] = query.message.text
    
    await query.edit_message_text(
        f"🔄 **بدء معالجة الطلب**\n\n"
        f"🆔 معرف الطلب: {order_id}\n\n"
        f"✅ **المتابعة مع معالجة الطلب:**",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    
    return PROCESS_ORDER

async def handle_direct_process_order(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالجة الطلب مباشرة بدون سؤال التحقق من الدفع"""
    try:
        query = update.callback_query
        await query.answer()
        
        # التحقق من وجود طلب قيد المعالجة (إنهاء الطلب السابق تلقائياً)
        current_processing_order = context.user_data.get('processing_order_id')
        if current_processing_order:
            # تنظيف الطلب السابق تلقائياً
            try:
                # إعادة الطلب السابق إلى حالة pending إذا لم يكتمل
                db.execute_query(
                    "UPDATE orders SET status = 'pending' WHERE id = ? AND status != 'completed'",
                    (current_processing_order,)
                )
                
                # تنظيف البيانات المؤقتة للطلب السابق
                context.user_data.pop('waiting_for_direct_admin_message', None)
                context.user_data.pop('waiting_for_admin_message', None)
                context.user_data.pop('direct_processing', None)
                context.user_data.pop('admin_processing_active', None)
                
                logger.info(f"تم تنظيف الطلب السابق {current_processing_order} تلقائياً لبدء طلب جديد")
            except Exception as e:
                logger.error(f"خطأ في تنظيف الطلب السابق: {e}")
                
            # إشعار بسيط للأدمن (اختياري)
            await query.answer(f"تم إنهاء الطلب السابق {current_processing_order[:8]}... تلقائياً", show_alert=False)
        
        order_id = query.data.replace("direct_process_", "")
        
        # التحقق من صحة معرف الطلب
        if not order_id:
            await query.edit_message_text("❌ خطأ: معرف الطلب غير صحيح")
            await restore_admin_keyboard(context, update.effective_chat.id)
            return
        
        # التحقق من وجود الطلب في قاعدة البيانات
        order_check = db.execute_query("SELECT id FROM orders WHERE id = ?", (order_id,))
        if not order_check:
            await query.edit_message_text(f"❌ خطأ: لم يتم العثور على الطلب {order_id}")
            await restore_admin_keyboard(context, update.effective_chat.id)
            return
        
        # تسجيل بداية معالجة طلب جديد
        context.user_data['processing_order_id'] = order_id
        context.user_data['admin_processing_active'] = True
        context.user_data['direct_processing'] = True  # علامة للمعالجة المباشرة
        
        # حفظ الرسالة الأصلية قبل التعديل
        context.user_data['original_order_message'] = query.message.text
        
        # معالجة مباشرة للطلب بدون conversation handler
        await handle_direct_payment_success(update, context)
        
    except Exception as e:
        logger.error(f"خطأ في handle_direct_process_order: {e}")
        try:
            error_details = f"❌ حدث خطأ في معالجة الطلب مباشرة\n\n🔍 التفاصيل التقنية:\n• معرف الطلب: {query.data.replace('direct_process_', '') if hasattr(query, 'data') else 'غير معروف'}\n• سبب الخطأ: {str(e)[:200]}...\n\n🔧 تم إعادة توجيهك للقائمة الرئيسية"
            await restore_admin_keyboard(context, update.effective_chat.id, error_details)
        except Exception as fallback_error:
            logger.error(f"خطأ في fallback لـ handle_direct_process_order: {fallback_error}")
            await restore_admin_keyboard(context, update.effective_chat.id)

async def handle_direct_payment_success(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالجة نجاح الدفع للمعالجة المباشرة (بدون conversation handler)"""
    query = update.callback_query
    
    order_id = context.user_data['processing_order_id']
    
    # توليد رقم المعاملة وحفظها (بدون تحديث حالة الطلب)
    transaction_number = generate_transaction_number('proxy')
    save_transaction(order_id, transaction_number, 'proxy', 'completed')
    
    # إرسال رسالة للمستخدم أن الطلب قيد المعالجة
    order_query = "SELECT user_id, proxy_type, payment_amount FROM orders WHERE id = ?"
    order_result = db.execute_query(order_query, (order_id,))
    if order_result:
        user_id = order_result[0][0]
        order_type = order_result[0][1]
        payment_amount = order_result[0][2] if len(order_result[0]) > 2 else 0.0
        user_language = get_user_language(user_id)
        
        # التحقق من كفاية الرصيد قبل خصم النقاط
        try:
            user_balance = db.get_user_balance(user_id)
            available_points = user_balance['charged_balance']
            
            if available_points < payment_amount:
                # رصيد غير كافي - تصنيف الطلب كفاشل
                db.execute_query("UPDATE orders SET status = 'failed' WHERE id = ?", (order_id,))
                
                # إشعار للمستخدم بالرفض
                if user_language == 'ar':
                    failure_message = f"""⚠️ مشكلة في خصم النقاط!

🆔 معرف الطلب: {order_id}
👤 معرف المستخدم: {user_id}
💰 النقاط المطلوبة: {payment_amount:.2f}
❌ السبب: رصيد غير كافي

الرجاء مراجعة الطلب."""
                else:
                    failure_message = f"""❌ Insufficient points balance!

💰 Points required: {payment_amount:.2f} points
🆔 Order ID: {order_id}

📞 Please recharge your balance or contact admin."""
                
                await context.bot.send_message(user_id, failure_message, parse_mode='Markdown')
                
                # إشعار للأدمن
                admin_message = f"⚠️ مشكلة في خصم النقاط!\n\n🆔 معرف الطلب: {order_id}\n👤 معرف المستخدم: {user_id}\n💰 النقاط المطلوبة: {payment_amount:.2f}\n❌ السبب: رصيد غير كافي\n\nالرجاء مراجعة الطلب."
                await query.edit_message_text(admin_message, parse_mode='Markdown')
                return
                
            # خصم النقاط من رصيد المستخدم
            db.deduct_credits(user_id, payment_amount, 'purchase', order_id, f"شراء {order_type}")
            logger.info(f"تم خصم {payment_amount} نقطة من المستخدم {user_id} للطلب {order_id}")
            
        except Exception as deduction_error:
            # خطأ في خصم النقاط - تصنيف الطلب كفاشل
            logger.error(f"خطأ في خصم النقاط للطلب {order_id}: {deduction_error}")
            db.execute_query("UPDATE orders SET status = 'failed' WHERE id = ?", (order_id,))
            
            # إشعار للأدمن
            admin_error_message = f"❌ خطأ في خصم النقاط!\n\n🆔 معرف الطلب: {order_id}\n👤 معرف المستخدم: {user_id}\n💰 النقاط المطلوبة: {payment_amount:.2f}\n🚫 خطأ: {str(deduction_error)}\n\nتم تصنيف الطلب كفاشل."
            await query.edit_message_text(admin_error_message, parse_mode='Markdown')
            return
        
        # رسالة للمستخدم مع رقم المعاملة
        if user_language == 'ar':
            user_message = f"""✅ تم قبول معاملتك بنجاح!

🆔 معرف الطلب: {order_id}
💳 رقم المعاملة: `{transaction_number}`
📦 نوع الباكج: {order_type}
💰 قيمة الطلب: `{payment_amount}$`

🔄 سيتم معالجة طلبك وإرسال البيانات قريباً.
💎 سيتم خصم الكريديت عند إرسال بيانات البروكسي"""
        else:
            user_message = f"""✅ Your transaction has been accepted successfully!

🆔 Order ID: {order_id}
💳 Transaction Number: `{transaction_number}`
📦 Package Type: {order_type}
💰 Order Value: `{payment_amount}$`

🔄 Your order will be processed and data sent soon.
💎 Credits will be deducted when proxy data is sent"""
        
        await context.bot.send_message(user_id, user_message, parse_mode='Markdown')
        
        # التحقق من نوع الطلب
        if order_type == 'withdrawal':
            # معالجة طلب السحب
            await handle_withdrawal_approval_direct(query, context, order_id, user_id)
            return
    
    # رسالة للأدمن مع رقم المعاملة ونوع البروكسي
    static_type = context.user_data.get('static_type', '')
    if order_type == "static":
        if static_type == 'residential_verizon':
            proxy_type_ar = "ريزيدنتال Crocker (4$)"
        elif static_type == 'residential_att':
            proxy_type_ar = "ريزيدنتال"
        elif static_type == 'isp':
            proxy_type_ar = "ISP (3$)"
        else:
            proxy_type_ar = "بروكسي ستاتيك"
    elif order_type == "socks":
        proxy_type_ar = "بروكسي سوكس"
    else:
        proxy_type_ar = order_type
    
    admin_message = f"""✅ تم قبول الدفع للطلب

🆔 معرف الطلب: {order_id}
💳 رقم المعاملة: `{transaction_number}`
👤 معرف المستخدم: `{user_id}`
📝 الطلب: {proxy_type_ar}
💰 قيمة الطلب: `{payment_amount}$`

📋 الطلب جاهز للمعالجة والإرسال للمستخدم."""
    
    # تحضير رسالة انتظار الأدمن بدون conversation handler
    keyboard = [
        [InlineKeyboardButton("🔙 رجوع", callback_data="cancel_direct_processing")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # استخدام الرسالة الأصلية مع إضافة معلومات الدفع وتحضير للرد المباشر
    original_message = context.user_data.get('original_order_message', '')
    combined_message = f"{original_message}\n\n━━━━━━━━━━━━━━━\n{admin_message}\n\n━━━━━━━━━━━━━━━\n📝 **اكتب رسالتك الآن للمستخدم:**\n\n⬇️ *اكتب رسالة نصية وسيتم إرسالها للمستخدم مع تفاصيل البروكسي*"
    
    # التحقق من طول الرسالة
    if len(combined_message) > 4000:  # حد أمان أقل من حد Telegram (4096)
        # استخدام رسالة مختصرة
        combined_message = f"✅ تم قبول الدفع للطلب\n\n🆔 معرف الطلب: {order_id}\n💰 قيمة الطلب: `{payment_amount}$`\n\n📋 الطلب جاهز للمعالجة والإرسال للمستخدم.\n\n━━━━━━━━━━━━━━━\n📝 **اكتب رسالتك الآن للمستخدم:**\n\n⬇️ *اكتب رسالة نصية وسيتم إرسالها للمستخدم مع تفاصيل البروكسي*"
    
    try:
        await query.edit_message_text(
            combined_message,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    except Exception as e:
        # محاولة بديلة بدون parse_mode
        try:
            await query.edit_message_text(
                combined_message,
                reply_markup=reply_markup
            )
        except Exception as e2:
            print(f"❌ خطأ في المحاولة البديلة: {e2}")
    
    # تعيين علامة انتظار رسالة الأدمن للمعالجة المباشرة
    context.user_data['waiting_for_direct_admin_message'] = True

async def handle_withdrawal_approval_direct(query, context: ContextTypes.DEFAULT_TYPE, order_id: str, user_id: int) -> None:
    """معالجة طلب السحب مع خيارات النجاح/الفشل للمعالجة المباشرة"""
    
    # إنشاء أزرار النجاح والفشل
    keyboard = [
        [InlineKeyboardButton("✅ تم التسديد", callback_data=f"withdrawal_success_{order_id}")],
        [InlineKeyboardButton("❌ فشلت المعاملة", callback_data=f"withdrawal_failed_{order_id}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"💰 معالجة طلب سحب الرصيد\n\n🆔 معرف الطلب: {order_id}\n\nاختر حالة المعاملة:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def handle_back_to_pending_orders(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """العودة إلى قائمة الطلبات المعلقة"""
    try:
        query = update.callback_query
        await query.answer()
        
        # إعادة عرض الطلبات المعلقة
        pending_orders = db.get_pending_orders()
        
        if not pending_orders:
            await query.edit_message_text("✅ لا توجد طلبات معلقة حالياً.")
            return
        
        total_orders = len(pending_orders)
        
        # إنشاء أزرار لعرض تفاصيل كل طلب
        keyboard = []
        for i, order in enumerate(pending_orders[:20], 1):  # عرض أول 20 طلب لتجنب تجاوز حدود التيليجرام
            try:
                # التحقق من صحة بيانات الطلب قبل المعالجة
                order_id = str(order[0]) if order[0] else "unknown"
                proxy_type = str(order[2]) if len(order) > 2 and order[2] else "unknown"
                amount = str(order[6]) if len(order) > 6 and order[6] else "0"
                
                # عرض معلومات مختصرة في النص
                button_text = f"{i}. {order_id[:8]}... ({proxy_type} - {amount}$)"
                keyboard.append([InlineKeyboardButton(button_text, callback_data=f"view_pending_order_{order_id}")])
            except Exception as order_error:
                logger.error(f"Error processing pending order {i} in back navigation: {order_error}")
                # إضافة زر للطلب التالف مع معلومات أساسية
                keyboard.append([InlineKeyboardButton(f"{i}. طلب تالف - إصلاح مطلوب", callback_data=f"fix_order_{i}")])
        
        # إضافة زر لعرض المزيد إذا كان هناك أكثر من 20 طلب
        if total_orders > 20:
            keyboard.append([InlineKeyboardButton(f"عرض المزيد... ({total_orders - 20} طلب إضافي)", callback_data="show_more_pending")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        message = f"📋 **الطلبات المعلقة** - المجموع: {total_orders} طلب\n\n🔽 اختر طلباً لعرض تفاصيله الكاملة مع إثبات الدفع:"
        
        await query.edit_message_text(message, parse_mode='Markdown', reply_markup=reply_markup)
        
    except Exception as e:
        logger.error(f"Error in handle_back_to_pending_orders: {e}")
        print(f"❌ خطأ في العودة للطلبات المعلقة: {e}")
        
        # محاولة إرسال رسالة خطأ مع خيارات
        try:
            # التحقق من صحة البيانات المطلوبة
            if not query or not hasattr(query, 'edit_message_text'):
                raise Exception("Query object is invalid")
                
            keyboard = [
                [InlineKeyboardButton("🔄 إعادة المحاولة", callback_data="retry_pending_orders")],
                [InlineKeyboardButton("🗃️ إدارة قاعدة البيانات", callback_data="admin_database_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                "❌ حدث خطأ في تحميل الطلبات المعلقة\n\n"
                "الرجاء اختيار إجراء:",
                reply_markup=reply_markup
            )
        except Exception as msg_error:
            logger.error(f"Failed to send error message in back navigation: {msg_error}")
            # محاولة إرسال رسالة بسيطة بدون أزرار
            try:
                await query.edit_message_text("❌ حدث خطأ في تحميل الطلبات المعلقة")
                await asyncio.sleep(2)
                await restore_admin_keyboard(context, update.effective_chat.id)
            except Exception as final_error:
                logger.error(f"Final fallback failed: {final_error}")
                # العودة للوحة الأدمن الرئيسية كحل أخير
                await restore_admin_keyboard(context, update.effective_chat.id, "❌ حدث خطأ في النظام. تم إعادة تعيين الواجهة.")

async def handle_payment_success(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """معالجة نجاح الدفع والبدء في جمع معلومات البروكسي"""
    query = update.callback_query
    await query.answer()
    
    order_id = context.user_data['processing_order_id']
    
    # الحصول على تفاصيل الطلب أولاً
    order_query = "SELECT user_id, proxy_type, payment_amount FROM orders WHERE id = ?"
    order_result = db.execute_query(order_query, (order_id,))
    if not order_result:
        await query.edit_message_text("❌ خطأ: لم يتم العثور على الطلب")
        return ConversationHandler.END
        
    user_id = order_result[0][0]
    order_type = order_result[0][1]
    payment_amount = order_result[0][2] if order_result[0][2] else 0.0
    user_language = get_user_language(user_id)
    
    # فحص كفاية الرصيد قبل البدء في المعالجة (للبروكسيات فقط)
    if order_type in ['static', 'socks']:
        balance = db.get_user_balance(user_id)
        total_balance = balance['total_balance']
        
        if total_balance < payment_amount:
            # فشل الطلب بسبب عدم كفاية الرصيد
            db.execute_query("UPDATE orders SET status = 'failed' WHERE id = ?", (order_id,))
            
            # إشعار المستخدم بفشل الطلب
            if user_language == 'ar':
                insufficient_message = f"""❌ فشل في معالجة طلبك بسبب عدم كفاية الرصيد!

💰 رصيدك الحالي: {total_balance:.2f} نقطة
💵 المطلوب: {payment_amount:.2f} نقطة
🆔 معرف الطلب: {order_id}

📞 يرجى شحن رصيدك أولاً ثم إعادة الطلب."""
            else:
                insufficient_message = f"""❌ Order failed due to insufficient balance!

💰 Your current balance: {total_balance:.2f} points
💵 Required: {payment_amount:.2f} points
🆔 Order ID: {order_id}

📞 Please recharge your balance first and try again."""
            
            await context.bot.send_message(user_id, insufficient_message, parse_mode='Markdown')
            
            # إشعار الأدمن بفشل الطلب
            admin_message = f"""❌ فشل طلب بسبب عدم كفاية الرصيد

🆔 معرف الطلب: {order_id}
👤 معرف المستخدم: {user_id}
💰 رصيد المستخدم: {total_balance:.2f} نقطة
💵 المطلوب: {payment_amount:.2f} نقطة

تم إلغاء الطلب تلقائياً."""
            
            await query.edit_message_text(admin_message, parse_mode='Markdown')
            return ConversationHandler.END
    
    # توليد رقم المعاملة وحفظها (بدون تحديث حالة الطلب)
    transaction_number = generate_transaction_number('proxy')
    save_transaction(order_id, transaction_number, 'proxy', 'completed')
    
    # رسالة للمستخدم مع رقم المعاملة
    if user_language == 'ar':
        user_message = f"""✅ تم قبول معاملتك بنجاح!

🆔 معرف الطلب: {order_id}
💳 رقم المعاملة: `{transaction_number}`
📦 نوع الباكج: {order_type}
💰 قيمة الطلب: `{payment_amount}$`

🔄 سيتم معالجة طلبك وإرسال البيانات قريباً.
💎 سيتم خصم الكريديت عند إرسال بيانات البروكسي"""
    else:
        user_message = f"""✅ Your transaction has been accepted successfully!

🆔 Order ID: {order_id}
💳 Transaction Number: `{transaction_number}`
📦 Package Type: {order_type}
💰 Order Value: `{payment_amount}$`

🔄 Your order will be processed and data sent soon.
💎 Credits will be deducted when proxy data is sent"""
    
    await context.bot.send_message(user_id, user_message, parse_mode='Markdown')
    
    # ملاحظة: تم نقل خصم النقاط لتتم عند إرسال بيانات البروكسي فقط
    
    # التحقق من نوع الطلب
    if order_type == 'withdrawal':
        # معالجة طلب السحب
        await handle_withdrawal_approval(query, context, order_id, user_id)
        return ConversationHandler.END
    
    # رسالة للأدمن مع رقم المعاملة ونوع البروكسي
    static_type = context.user_data.get('static_type', '')
    if order_type == "static":
        if static_type == 'residential_verizon':
            proxy_type_ar = "ريزيدنتال Crocker (4$)"
        elif static_type == 'residential_att':
            proxy_type_ar = "ريزيدنتال"
        elif static_type == 'isp':
            proxy_type_ar = "ISP (3$)"
        else:
            proxy_type_ar = "بروكسي ستاتيك"
    elif order_type == "socks":
        proxy_type_ar = "بروكسي سوكس"
    else:
        proxy_type_ar = order_type
    
    admin_message = f"""✅ تم قبول الدفع للطلب

🆔 معرف الطلب: {order_id}
💳 رقم المعاملة: `{transaction_number}`
👤 معرف المستخدم: `{user_id}`
📝 الطلب: {proxy_type_ar}
💰 قيمة الطلب: `{payment_amount}$`

📋 الطلب جاهز للمعالجة والإرسال للمستخدم."""
    
    # تجاوز أزرار الكمية والانتقال مباشرة لانتظار رسالة الأدمن
    keyboard = [
        [InlineKeyboardButton("🔙 رجوع", callback_data="cancel_processing")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # استخدام الرسالة الأصلية مع إضافة معلومات الدفع وتحضير للرد المباشر
    original_message = context.user_data.get('original_order_message', '')
    combined_message = f"{original_message}\n\n━━━━━━━━━━━━━━━\n{admin_message}\n\n━━━━━━━━━━━━━━━\n📝 **اكتب رسالتك الآن للمستخدم:**\n\n⬇️ *اكتب رسالة نصية وسيتم إرسالها للمستخدم مع تفاصيل البروكسي*"
    
    # التحقق من طول الرسالة
    print(f"📏 طول الرسالة: {len(combined_message)} حرف")
    if len(combined_message) > 4000:  # حد أمان أقل من حد Telegram (4096)
        print("⚠️ الرسالة طويلة جداً، سيتم تقصيرها")
        # استخدام رسالة مختصرة
        combined_message = f"✅ تم قبول الدفع للطلب\n\n🆔 معرف الطلب: `{context.user_data['processing_order_id']}`\n💰 قيمة الطلب: `{payment_amount}$`\n\n📋 الطلب جاهز للمعالجة والإرسال للمستخدم.\n\n━━━━━━━━━━━━━━━\n📝 **اكتب رسالتك الآن للمستخدم:**\n\n⬇️ *اكتب رسالة نصية وسيتم إرسالها للمستخدم مع تفاصيل البروكسي*"
    
    try:
        print(f"🔄 محاولة تحديث الرسالة")
        await query.edit_message_text(
            combined_message,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        print(f"✅ تم تحديث الرسالة بنجاح - ينتظر رسالة الأدمن")
    except Exception as e:
        print(f"❌ خطأ في تحديث الرسالة: {e}")
        # محاولة بديلة بدون parse_mode
        try:
            await query.edit_message_text(
                combined_message,
                reply_markup=reply_markup
            )
            print(f"✅ تم تحديث الرسالة بنجاح بدون parse_mode - ينتظر رسالة الأدمن")
        except Exception as e2:
            print(f"❌ خطأ في المحاولة البديلة: {e2}")
    
    # الانتقال مباشرة لحالة انتظار رسالة الأدمن
    context.user_data['waiting_for_admin_message'] = True
    # تعيين الوضع كـ "نجاح" لمنع التداخل مع تدفق الفشل
    context.user_data['custom_mode'] = 'success'
    return CUSTOM_MESSAGE

async def handle_send_direct_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """معالجة إرسال رسالة مباشرة للمستخدم"""
    query = update.callback_query
    await query.answer()
    
    order_id = query.data.replace("send_direct_message_", "")
    context.user_data['direct_message_order_id'] = order_id
    
    # تحديث الرسالة لإظهار حالة انتظار الرسالة
    await query.edit_message_text(
        f"💬 إرسال رسالة مباشرة للمستخدم\n\n🆔 معرف الطلب: {order_id}\n\n📝 اكتب رسالتك الآن وسيتم إرسالها مباشرة للمستخدم:",
        parse_mode='Markdown'
    )
    
    # تحديد حالة انتظار رسالة الأدمن
    context.user_data['waiting_for_admin_message'] = True
    
    return PROCESS_ORDER

async def handle_withdrawal_approval(query, context: ContextTypes.DEFAULT_TYPE, order_id: str, user_id: int) -> None:
    """معالجة طلب السحب مع خيارات النجاح/الفشل"""
    
    # إنشاء أزرار النجاح والفشل
    keyboard = [
        [InlineKeyboardButton("✅ تم التسديد", callback_data=f"withdrawal_success_{order_id}")],
        [InlineKeyboardButton("❌ فشلت المعاملة", callback_data=f"withdrawal_failed_{order_id}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"💰 معالجة طلب سحب الرصيد\n\n🆔 معرف الطلب: {order_id}\n\nاختر حالة المعاملة:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def handle_payment_failed(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """معالجة فشل الدفع"""
    query = update.callback_query
    await query.answer()
    
    order_id = context.user_data['processing_order_id']
    
    # التحقق من أن الطلب لم يعد معالجاً من قبل
    check_query = "SELECT truly_processed FROM orders WHERE id = ?"
    check_result = db.execute_query(check_query, (order_id,))
    if check_result and check_result[0][0]:  # إذا كان معالجاً من قبل
        await query.edit_message_text(f"❌ الطلب {order_id} تم معالجته بالفعل ولا يمكن تعديله.")
        await restore_admin_keyboard(context, update.effective_chat.id)
        return ConversationHandler.END
    
    # توليد رقم المعاملة وحفظها
    transaction_number = generate_transaction_number('proxy')
    save_transaction(order_id, transaction_number, 'proxy', 'failed')
    
    # تحديث حالة الطلب إلى فاشل وتسجيله كمعالج فعلياً (الحالة الوحيدة للفشل: ضغط زر "لا")
    update_order_status(order_id, 'failed')
    
    # تسجيل الطلب كمعالج فعلياً لأن الأدمن أكد أن الدفع غير حقيقي أو فاشل
    db.execute_query(
        "UPDATE orders SET truly_processed = TRUE WHERE id = ?",
        (order_id,)
    )
    
    # إرسال رسالة للمستخدم
    order_query = "SELECT user_id, proxy_type FROM orders WHERE id = ?"
    order_result = db.execute_query(order_query, (order_id,))
    if order_result:
        user_id = order_result[0][0]
        order_type = order_result[0][1]
        user_language = get_user_language(user_id)
        
        # رسالة للمستخدم مع رقم المعاملة
        if user_language == 'ar':
            user_message = f"""❌ تم رفض دفعتك

🆔 معرف الطلب: {order_id}
💳 رقم المعاملة: `{transaction_number}`
📦 نوع الباكج: {order_type}

📞 يرجى التواصل مع الإدارة لمعرفة سبب الرفض."""
        else:
            user_message = f"""❌ Your payment has been rejected

🆔 Order ID: {order_id}
💳 Transaction Number: `{transaction_number}`
📦 Package Type: {order_type}

📞 Please contact admin to know the reason for rejection."""
        
        await context.bot.send_message(user_id, user_message, parse_mode='Markdown')
        
        # رسالة للأدمن مع رقم المعاملة ونوع البروكسي
        proxy_type_ar = "بروكسي ستاتيك" if order_type == "static" else "بروكسي سوكس" if order_type == "socks" else order_type
        
        admin_message = f"""❌ تم رفض الدفع للطلب

🆔 معرف الطلب: {order_id}
💳 رقم المعاملة: `{transaction_number}`
👤 معرف المستخدم: `{user_id}`
📝 الطلب: {proxy_type_ar}

📋 تم نقل الطلب إلى الطلبات الفاشلة وإشعار المستخدم بالرفض."""
    
    # تنظيف البيانات المؤقتة
    context.user_data.pop('processing_order_id', None)
    context.user_data.pop('admin_processing_active', None)
    context.user_data.pop('waiting_for_admin_message', None)
    context.user_data.pop('direct_processing', None)
    context.user_data.pop('custom_mode', None)
    
    await query.edit_message_text(
        admin_message,
        parse_mode='Markdown'
    )
    
    # إعادة تفعيل كيبورد الأدمن الرئيسي
    await restore_admin_keyboard(context, update.effective_chat.id)
    
    return ConversationHandler.END

async def handle_admin_menu_actions(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالجة إجراءات لوحة الأدمن"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "admin_referrals":
        await show_admin_referrals(query, context)
    
    elif query.data == "user_lookup":
        context.user_data['lookup_action'] = 'lookup'
        await query.edit_message_text("يرجى إرسال معرف المستخدم أو @username للبحث:")
        return USER_LOOKUP

async def show_admin_referrals(query, context: ContextTypes.DEFAULT_TYPE) -> None:
    """عرض إحصائيات الإحالات للأدمن"""
    # إحصائيات الإحالات
    total_referrals = db.execute_query("SELECT COUNT(*) FROM referrals")[0][0]
    total_amount = db.execute_query("SELECT SUM(amount) FROM referrals")[0][0] or 0
    
    # أفضل المحيلين
    top_referrers = db.execute_query('''
        SELECT u.first_name, u.last_name, COUNT(r.id) as referral_count, SUM(r.amount) as total_earned
        FROM users u
        JOIN referrals r ON u.user_id = r.referrer_id
        GROUP BY u.user_id
        ORDER BY referral_count DESC
        LIMIT 5
    ''')
    
    message = f"📊 إحصائيات الإحالات\n\n"
    message += f"إجمالي الإحالات: {total_referrals}\n"
    message += f"إجمالي المبلغ: {total_amount:.2f}$\n\n"
    message += "أفضل المحيلين:\n"
    
    for i, referrer in enumerate(top_referrers, 1):
        message += f"{i}. {referrer[0]} {referrer[1]}: {referrer[2]} إحالة ({referrer[3]:.2f}$)\n"
    
    keyboard = [
        [InlineKeyboardButton("تحديد قيمة الإحالة", callback_data="set_referral_amount")],
        [InlineKeyboardButton("تصفير رصيد مستخدم", callback_data="reset_user_balance")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(message, reply_markup=reply_markup)

async def handle_proxy_details_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """معالجة إدخال تفاصيل البروكسي خطوة بخطوة"""
    query = update.callback_query
    
    if query:
        await query.answer()
        
        if query.data.startswith("proxy_type_"):
            proxy_type = query.data.replace("proxy_type_", "")
            context.user_data['admin_proxy_type'] = proxy_type
            context.user_data['admin_input_state'] = ENTER_PROXY_ADDRESS
            
            keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data="cancel_proxy_setup")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            message = await query.edit_message_text("2️⃣ يرجى إدخال عنوان البروكسي:", reply_markup=reply_markup)
            # حفظ معرف الرسالة الحالية للتحديث لاحقاً
            context.user_data['last_cancel_message_id'] = message.message_id
            return ENTER_PROXY_ADDRESS
    
    else:
        # معالجة النص المدخل
        text = update.message.text
        

        
        current_state = context.user_data.get('admin_input_state', ENTER_PROXY_ADDRESS)
        
        if current_state == ENTER_PROXY_ADDRESS:
            # التحقق من صحة عنوان IP
            if not validate_ip_address(text):
                keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data="cancel_proxy_setup")]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                message = await update.message.reply_text(
                    "❌ عنوان IP غير صحيح!\n\n"
                    "✅ الشكل المطلوب: xxx.xxx.xxx.xxx\n"
                    "✅ مثال صحيح: 192.168.1.1 أو 62.1.2.1\n"
                    "✅ يُقبل من 1-3 أرقام لكل جزء\n\n"
                    "يرجى إعادة إدخال عنوان IP:",
                    reply_markup=reply_markup
                )
                # حفظ معرف رسالة الخطأ أيضاً
                context.user_data['last_cancel_message_id'] = message.message_id
                return ENTER_PROXY_ADDRESS
            
            context.user_data['admin_proxy_address'] = text
            context.user_data['admin_input_state'] = ENTER_PROXY_PORT
            
            # تحديث الرسالة السابقة لإزالة زر الإلغاء
            try:
                last_message_id = context.user_data.get('last_cancel_message_id')
                if last_message_id:
                    await context.bot.edit_message_text(
                        chat_id=update.effective_chat.id,
                        message_id=last_message_id,
                        text="2️⃣ ✅ تم حفظ عنوان البروكسي: " + text
                    )
            except:
                # في حالة فشل التحديث، إرسال رسالة تأكيد منفصلة
                await update.message.reply_text("✅ تم حفظ عنوان البروكسي: " + text)
            
            keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data="cancel_proxy_setup")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            message = await update.message.reply_text("3️⃣ يرجى إدخال البورت:", reply_markup=reply_markup)
            # حفظ معرف الرسالة الجديدة
            context.user_data['last_cancel_message_id'] = message.message_id
            return ENTER_PROXY_PORT
        
        elif current_state == ENTER_PROXY_PORT:
            # التحقق من صحة البورت
            if not validate_port(text):
                keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data="cancel_proxy_setup")]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                message = await update.message.reply_text(
                    "❌ رقم البورت غير صحيح!\n\n"
                    "✅ يجب أن يكون رقماً فقط\n"
                    "✅ حد أقصى 6 أرقام\n"
                    "✅ مثال صحيح: 80, 8080, 123456\n\n"
                    "يرجى إعادة إدخال رقم البورت:",
                    reply_markup=reply_markup
                )
                # حفظ معرف رسالة الخطأ أيضاً
                context.user_data['last_cancel_message_id'] = message.message_id
                return ENTER_PROXY_PORT
            
            context.user_data['admin_proxy_port'] = text
            
            # تحديث الرسالة السابقة لإزالة زر الإلغاء
            try:
                last_message_id = context.user_data.get('last_cancel_message_id')
                if last_message_id:
                    await context.bot.edit_message_text(
                        chat_id=update.effective_chat.id,
                        message_id=last_message_id,
                        text="3️⃣ ✅ تم حفظ البورت: " + text
                    )
            except:
                # في حالة فشل التحديث، إرسال رسالة تأكيد منفصلة
                await update.message.reply_text("✅ تم حفظ البورت: " + text)
            
            # تحديد نوع البروكسي المختار لعرض الدول المناسبة
            proxy_type = context.user_data.get('admin_proxy_type', 'static')
            if proxy_type == 'socks':
                countries = SOCKS_COUNTRIES['ar']
            else:
                countries = STATIC_COUNTRIES['ar']
            
            # عرض قائمة الدول مقسمة
            reply_markup = create_paginated_keyboard(countries, "admin_country_", 0, 8, 'ar')
            await update.message.reply_text("4️⃣ اختر الدولة:", reply_markup=reply_markup)
            return ENTER_COUNTRY
        
        elif current_state == ENTER_COUNTRY:
            # معالجة إدخال الدولة يدوياً
            context.user_data['admin_proxy_country'] = text
            context.user_data['admin_input_state'] = ENTER_STATE
            
            # تأكيد حفظ الدولة
            try:
                await update.message.reply_text("✅ تم حفظ الدولة: " + text)
            except:
                pass
            
            keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data="cancel_proxy_setup")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            message = await update.message.reply_text("5️⃣ يرجى إدخال اسم الولاية:", reply_markup=reply_markup)
            # حفظ معرف الرسالة الجديدة
            context.user_data['last_cancel_message_id'] = message.message_id
            return ENTER_STATE
        
        elif current_state == ENTER_STATE:
            # معالجة إدخال الولاية يدوياً
            context.user_data['admin_proxy_state'] = text
            context.user_data['admin_input_state'] = ENTER_USERNAME
            
            # تحديث الرسالة السابقة لإزالة زر الإلغاء
            try:
                last_message_id = context.user_data.get('last_cancel_message_id')
                if last_message_id:
                    await context.bot.edit_message_text(
                        chat_id=update.effective_chat.id,
                        message_id=last_message_id,
                        text="5️⃣ ✅ تم حفظ الولاية: " + text
                    )
            except:
                # في حالة فشل التحديث، إرسال رسالة تأكيد منفصلة
                await update.message.reply_text("✅ تم حفظ الولاية: " + text)
            
            keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data="cancel_proxy_setup")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            message = await update.message.reply_text("6️⃣ يرجى إدخال اسم المستخدم للبروكسي:", reply_markup=reply_markup)
            # حفظ معرف الرسالة الجديدة
            context.user_data['last_cancel_message_id'] = message.message_id
            return ENTER_USERNAME
        
        elif current_state == ENTER_USERNAME:
            context.user_data['admin_proxy_username'] = text
            context.user_data['admin_input_state'] = ENTER_PASSWORD
            
            # تحديث الرسالة السابقة لإزالة زر الإلغاء
            try:
                last_message_id = context.user_data.get('last_cancel_message_id')
                if last_message_id:
                    await context.bot.edit_message_text(
                        chat_id=update.effective_chat.id,
                        message_id=last_message_id,
                        text="6️⃣ ✅ تم حفظ اسم المستخدم: " + text
                    )
            except:
                # في حالة فشل التحديث، إرسال رسالة تأكيد منفصلة
                await update.message.reply_text("✅ تم حفظ اسم المستخدم: " + text)
            
            keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data="cancel_proxy_setup")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            message = await update.message.reply_text("7️⃣ يرجى إدخال كلمة المرور:", reply_markup=reply_markup)
            # حفظ معرف الرسالة الجديدة
            context.user_data['last_cancel_message_id'] = message.message_id
            return ENTER_PASSWORD
        
        elif current_state == ENTER_PASSWORD:
            context.user_data['admin_proxy_password'] = text
            context.user_data['admin_input_state'] = ENTER_THANK_MESSAGE
            
            # تحديث الرسالة السابقة لإزالة زر الإلغاء
            try:
                last_message_id = context.user_data.get('last_cancel_message_id')
                if last_message_id:
                    await context.bot.edit_message_text(
                        chat_id=update.effective_chat.id,
                        message_id=last_message_id,
                        text="7️⃣ ✅ تم حفظ كلمة المرور بنجاح"
                    )
            except:
                # في حالة فشل التحديث، إرسال رسالة تأكيد منفصلة
                await update.message.reply_text("✅ تم حفظ كلمة المرور بنجاح")
            
            keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data="cancel_proxy_setup")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            message = await update.message.reply_text("8️⃣ يرجى إدخال رسالة شكر قصيرة:", reply_markup=reply_markup)
            # حفظ معرف الرسالة الجديدة
            context.user_data['last_cancel_message_id'] = message.message_id
            return ENTER_THANK_MESSAGE
        
        elif current_state == ENTER_THANK_MESSAGE:
            thank_message = text
            context.user_data['admin_thank_message'] = thank_message
            
            # تحديث الرسالة السابقة لإزالة زر الإلغاء
            try:
                last_message_id = context.user_data.get('last_cancel_message_id')
                if last_message_id:
                    await context.bot.edit_message_text(
                        chat_id=update.effective_chat.id,
                        message_id=last_message_id,
                        text="8️⃣ ✅ تم حفظ رسالة الشكر بنجاح"
                    )
            except:
                # في حالة فشل التحديث، إرسال رسالة تأكيد منفصلة
                await update.message.reply_text("✅ تم حفظ رسالة الشكر بنجاح")
            
            # عرض المعلومات للمراجعة قبل الإرسال
            await show_proxy_preview(update, context)
            return ENTER_THANK_MESSAGE
    
    return current_state

async def send_proxy_to_user(update: Update, context: ContextTypes.DEFAULT_TYPE, thank_message: str = None) -> None:
    """إرسال تفاصيل البروكسي للمستخدم"""
    order_id = context.user_data['processing_order_id']
    
    # الحصول على معلومات المستخدم والطلب
    user_query = """
        SELECT o.user_id, u.first_name, u.last_name 
        FROM orders o 
        JOIN users u ON o.user_id = u.user_id 
        WHERE o.id = ?
    """
    user_result = db.execute_query(user_query, (order_id,))
    
    if user_result:
        user_id, first_name, last_name = user_result[0]
        user_full_name = f"{first_name} {last_name or ''}".strip()
        
        # الحصول على التاريخ والوقت الحاليين
        from datetime import datetime
        now = datetime.now()
        current_date = now.strftime("%Y-%m-%d")
        current_time = now.strftime("%H:%M:%S")
        
        # إنشاء رسالة البروكسي للمستخدم
        proxy_message = f"""✅ تم معالجة طلب {user_full_name}

🔐 تفاصيل البروكسي:
📡 العنوان: `{context.user_data['admin_proxy_address']}`
🔌 البورت: `{context.user_data['admin_proxy_port']}`
🌍 الدولة: {context.user_data.get('admin_proxy_country', 'غير محدد')}
🏠 الولاية: {context.user_data.get('admin_proxy_state', 'غير محدد')}
👤 اسم المستخدم: `{context.user_data['admin_proxy_username']}`
🔑 كلمة المرور: `{context.user_data['admin_proxy_password']}`

━━━━━━━━━━━━━━━
🆔 معرف الطلب: {order_id}
📅 التاريخ: {current_date}
🕐 الوقت: {current_time}

━━━━━━━━━━━━━━━
💬 {thank_message}"""
        
        # إرسال البروكسي للمستخدم
        await context.bot.send_message(user_id, proxy_message, parse_mode='Markdown')
        
        # تم حذف إرسال الرسالة المكررة - الرسالة ترسل مع البروكسي
        
        # تحديث حالة الطلب
        proxy_details = {
            'address': context.user_data['admin_proxy_address'],
            'port': context.user_data['admin_proxy_port'],
            'country': context.user_data.get('admin_proxy_country', ''),
            'state': context.user_data.get('admin_proxy_state', ''),
            'username': context.user_data['admin_proxy_username'],
            'password': context.user_data['admin_proxy_password']
        }
        
        # تسجيل الطلب كمكتمل ومعالج فعلياً (الشرط الثاني: إرسال البيانات الكاملة للمستخدم)
        db.execute_query(
            "UPDATE orders SET status = 'completed', processed_at = CURRENT_TIMESTAMP, proxy_details = ?, truly_processed = TRUE WHERE id = ?",
            (json.dumps(proxy_details), order_id)
        )
        
        # التحقق من إضافة رصيد الإحالة لأول عملية شراء
        await check_and_add_referral_bonus(context, user_id, order_id)
        
        # رسالة تأكيد للأدمن
        admin_message = f"""✅ تم معالجة طلب {user_full_name}

🔐 تفاصيل البروكسي المرسلة:
📡 العنوان: `{context.user_data['admin_proxy_address']}`
🔌 البورت: `{context.user_data['admin_proxy_port']}`
🌍 الدولة: {context.user_data.get('admin_proxy_country', 'غير محدد')}
🏠 الولاية: {context.user_data.get('admin_proxy_state', 'غير محدد')}
👤 اسم المستخدم: `{context.user_data['admin_proxy_username']}`
🔑 كلمة المرور: `{context.user_data['admin_proxy_password']}`

━━━━━━━━━━━━━━━
🆔 معرف الطلب: {order_id}
📅 التاريخ: {current_date}
🕐 الوقت: {current_time}

━━━━━━━━━━━━━━━
💬 {thank_message}"""

        await update.message.reply_text(admin_message, parse_mode='Markdown')
        
        # تنظيف البيانات المؤقتة
        admin_keys = [k for k in context.user_data.keys() if k.startswith('admin_')]
        for key in admin_keys:
            del context.user_data[key]
        
        # إزالة معرف الطلب قيد المعالجة لضمان إمكانية معالجة طلبات جديدة
        context.user_data.pop('processing_order_id', None)
        context.user_data.pop('admin_processing_active', None)

async def send_proxy_to_user_direct(update: Update, context: ContextTypes.DEFAULT_TYPE, thank_message: str = None) -> None:
    """إرسال تفاصيل البروكسي للمستخدم مباشرة"""
    order_id = context.user_data['processing_order_id']
    
    # الحصول على معلومات المستخدم والطلب
    user_query = """
        SELECT o.user_id, u.first_name, u.last_name 
        FROM orders o 
        JOIN users u ON o.user_id = u.user_id 
        WHERE o.id = ?
    """
    user_result = db.execute_query(user_query, (order_id,))
    
    if user_result:
        user_id, first_name, last_name = user_result[0]
        user_full_name = f"{first_name} {last_name or ''}".strip()
        
        # الحصول على التاريخ والوقت الحاليين
        from datetime import datetime
        now = datetime.now()
        current_date = now.strftime("%Y-%m-%d")
        current_time = now.strftime("%H:%M:%S")
        
        # إنشاء رسالة البروكسي للمستخدم
        proxy_message = f"""✅ تم معالجة طلب {user_full_name}

🔐 تفاصيل البروكسي:
📡 العنوان: `{context.user_data['admin_proxy_address']}`
🔌 البورت: `{context.user_data['admin_proxy_port']}`
🌍 الدولة: {context.user_data.get('admin_proxy_country', 'غير محدد')}
🏠 الولاية: {context.user_data.get('admin_proxy_state', 'غير محدد')}
👤 اسم المستخدم: `{context.user_data['admin_proxy_username']}`
🔑 كلمة المرور: `{context.user_data['admin_proxy_password']}`

━━━━━━━━━━━━━━━
🆔 معرف الطلب: {order_id}
📅 التاريخ: {current_date}
🕐 الوقت: {current_time}

━━━━━━━━━━━━━━━
💬 {thank_message}"""
        
        # اقتطاع الرصيد من المستخدم عند إرسال البروكسي (هذا هو التوقيت الصحيح)
        order_query = "SELECT user_id, payment_amount, proxy_type FROM orders WHERE id = ?"
        order_result = db.execute_query(order_query, (order_id,))
        
        if order_result:
            order_user_id, payment_amount, proxy_type = order_result[0]
            
            # اقتطاع الرصيد (مع السماح بالرصيد السالب لمنع التحايل)
            try:
                db.deduct_credits(
                    order_user_id, 
                    payment_amount, 
                    'proxy_purchase', 
                    order_id, 
                    f"شراء بروكسي {proxy_type}",
                    allow_negative=True  # السماح بالرصيد السالب
                )
                logger.info(f"تم اقتطاع {payment_amount} نقطة من المستخدم {order_user_id} للطلب {order_id}")
            except Exception as deduct_error:
                logger.error(f"Error deducting points for order {order_id}: {deduct_error}")
        
        # إرسال البروكسي للمستخدم
        await context.bot.send_message(user_id, proxy_message, parse_mode='Markdown')
        
        # تحديث حالة الطلب
        proxy_details = {
            'address': context.user_data['admin_proxy_address'],
            'port': context.user_data['admin_proxy_port'],
            'country': context.user_data.get('admin_proxy_country', ''),
            'state': context.user_data.get('admin_proxy_state', ''),
            'username': context.user_data['admin_proxy_username'],
            'password': context.user_data['admin_proxy_password']
        }
        
        # تسجيل الطلب كمكتمل ومعالج فعلياً (الشرط الثاني: إرسال البيانات الكاملة للمستخدم)
        db.execute_query(
            "UPDATE orders SET status = 'completed', processed_at = CURRENT_TIMESTAMP, proxy_details = ?, truly_processed = TRUE WHERE id = ?",
            (json.dumps(proxy_details), order_id)
        )
        
        # التحقق من إضافة رصيد الإحالة لأول عملية شراء
        await check_and_add_referral_bonus(context, user_id, order_id)
        
        # تنظيف البيانات المؤقتة (مطلوب لضمان عدم تعليق البوت)
        admin_keys = [k for k in context.user_data.keys() if k.startswith('admin_')]
        for key in admin_keys:
            context.user_data.pop(key, None)
        
        # إزالة معرف الطلب قيد المعالجة لضمان إمكانية معالجة طلبات جديدة
        context.user_data.pop('processing_order_id', None)
        context.user_data.pop('admin_processing_active', None)

async def handle_user_lookup(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """معالجة البحث عن مستخدم"""
    search_term = update.message.text
    
    # البحث بالمعرف أو اسم المستخدم
    if search_term.startswith('@'):
        username = search_term[1:]
        query = "SELECT * FROM users WHERE username = ?"
        user_result = db.execute_query(query, (username,))
    else:
        try:
            user_id = int(search_term)
            query = "SELECT * FROM users WHERE user_id = ?"
            user_result = db.execute_query(query, (user_id,))
        except ValueError:
            # إعادة تفعيل كيبورد الأدمن
            await update.message.reply_text("معرف المستخدم غير صحيح!")
            await restore_admin_keyboard(context, update.effective_chat.id, "🔧 لوحة الأدمن جاهزة")
            return ConversationHandler.END
    
    if not user_result:
        # إعادة تفعيل كيبورد الأدمن
        await update.message.reply_text("المستخدم غير موجود!")
        await restore_admin_keyboard(context, update.effective_chat.id, "🔧 لوحة الأدمن جاهزة")
        return ConversationHandler.END
    
    user = user_result[0]
    user_id = user[0]
    
    # إحصائيات المستخدم
    successful_orders = db.execute_query(
        "SELECT COUNT(*), SUM(payment_amount) FROM orders WHERE user_id = ? AND status = 'completed'",
        (user_id,)
    )[0]
    
    failed_orders = db.execute_query(
        "SELECT COUNT(*) FROM orders WHERE user_id = ? AND status = 'failed'",
        (user_id,)
    )[0][0]
    
    pending_orders = db.execute_query(
        "SELECT COUNT(*) FROM orders WHERE user_id = ? AND status = 'pending'",
        (user_id,)
    )[0][0]
    
    # إحصائيات إضافية للتشخيص
    all_orders = db.execute_query(
        "SELECT COUNT(*) FROM orders WHERE user_id = ?",
        (user_id,)
    )[0][0]
    
    # فحص الطلبات بحسب الحالة (للتشخيص)
    try:
        orders_by_status = db.execute_query(
            "SELECT status, COUNT(*), COALESCE(SUM(payment_amount), 0) FROM orders WHERE user_id = ? GROUP BY status",
            (user_id,)
        ) or []
    except:
        orders_by_status = []
    
    referral_count = db.execute_query(
        "SELECT COUNT(*) FROM referrals WHERE referrer_id = ?",
        (user_id,)
    )[0][0]
    
    last_successful_order = db.execute_query(
        "SELECT created_at FROM orders WHERE user_id = ? AND status = 'completed' ORDER BY created_at DESC LIMIT 1",
        (user_id,)
    )
    
    # الحصول على معلومات إضافية عن المستخدم
    # الرصيد الحالي (points)
    current_balance = float(user[6]) if user[6] else 0.0
    
    # الرصيد الإجمالي المكتسب من الإحالات
    referral_earned = float(user[5]) if user[5] else 0.0
    
    # إجمالي النقاط المشحونة (حساب بديل)
    try:
        total_recharged_result = db.execute_query(
            "SELECT COUNT(*) FROM orders WHERE user_id = ? AND status = 'completed'",
            (user_id,)
        )
        total_recharged = 0.0  # يمكن حسابها لاحقاً من بيانات أخرى
    except:
        total_recharged = 0.0
    
    # إجمالي النقاط المستخدمة (حساب بديل)
    try:
        total_spent_result = db.execute_query(
            "SELECT COALESCE(SUM(payment_amount), 0) FROM orders WHERE user_id = ? AND status = 'completed'",
            (user_id,)
        )
        total_spent = float(total_spent_result[0][0]) if total_spent_result and total_spent_result[0] else 0.0
    except:
        total_spent = 0.0
    
    # تحديد حالة المستخدم
    status_text = "🟢 نشط" if current_balance > 0 or all_orders > 0 else "🟡 غير نشط"
    
    report = f"""📊 ملف المستخدم الشامل

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👤 **البيانات الشخصية**
• الاسم: {user[2]} {user[3]}
• اسم المستخدم: @{user[1] or 'غير محدد'}  
• المعرف: `{user[0]}`
• الحالة: {status_text}
• تاريخ الانضمام: {user[7]}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💰 **النظام المالي**
• الرصيد الحالي: `${current_balance:.2f}`
• إجمالي الشحن: `${total_recharged:.2f}`
• إجمالي الإنفاق: `${total_spent:.2f}`
• رصيد الإحالات: `${referral_earned:.2f}`
• صافي الحساب: `${(current_balance + referral_earned):.2f}`

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📈 **إحصائيات الطلبات**
• إجمالي الطلبات: `{all_orders}`
• الطلبات الناجحة: `{successful_orders[0]}` (${successful_orders[1] or 0:.2f})
• الطلبات الفاشلة: `{failed_orders}`
• الطلبات المعلقة: `{pending_orders}`
• آخر شراء ناجح: {last_successful_order[0][0] if last_successful_order else 'لا يوجد'}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👥 **نظام الإحالات**
• عدد المُحالين: `{referral_count}` شخص
• أرباح الإحالات: `${referral_earned:.2f}`

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔍 **تفصيل الطلبات حسب الحالة:**
{chr(10).join([f"📌 **{status}**: {count} طلب → ${amount or 0:.2f}" for status, count, amount in orders_by_status]) if orders_by_status else "لا توجد طلبات"}"""

    # حفظ معرف المستخدم للعمليات التالية
    context.user_data['selected_user_id'] = user_id
    context.user_data['selected_user_data'] = user
    
    # إنشاء أزرار الإدارة
    keyboard = [
        [
            InlineKeyboardButton("👤 إدارة المستخدم", callback_data=f"manage_user_{user_id}"),
            InlineKeyboardButton("💰 إدارة النقاط", callback_data=f"manage_points_{user_id}")
        ],
        [
            InlineKeyboardButton("📢 بث لهذا المستخدم", callback_data=f"broadcast_user_{user_id}"),
            InlineKeyboardButton("👥 إدارة الإحالات", callback_data=f"manage_referrals_{user_id}")
        ],
        [
            InlineKeyboardButton("💬 انتقال للمحادثة", url=f"tg://user?id={user_id}"),
            InlineKeyboardButton("📊 تقارير مفصلة", callback_data=f"detailed_reports_{user_id}")
        ],
        [
            InlineKeyboardButton("🔙 رجوع لقائمة الأدمن", callback_data="back_to_admin_menu")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(report, reply_markup=reply_markup, parse_mode='Markdown')
    return ConversationHandler.END

# دوال إدارة المستخدمين الجديدة
async def handle_manage_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالجة إدارة المستخدم"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.data.split("_")[-1]
    user_data = context.user_data.get('selected_user_data')
    
    if not user_data:
        await query.edit_message_text("❌ خطأ: بيانات المستخدم غير متوفرة")
        return
    
    keyboard = [
        [
            InlineKeyboardButton("🚫 حظر المستخدم", callback_data=f"ban_user_{user_id}"),
            InlineKeyboardButton("✅ فك حظر المستخدم", callback_data=f"unban_user_{user_id}")
        ],
        [
            InlineKeyboardButton("🛠️ رفع الحظر المؤقت", callback_data=f"remove_temp_ban_{user_id}"),
            InlineKeyboardButton("📊 إعادة تعيين الإحصائيات", callback_data=f"reset_stats_{user_id}")
        ],
        [
            InlineKeyboardButton("🗑️ مسح البيانات", callback_data=f"delete_user_data_{user_id}"),
            InlineKeyboardButton("🔙 رجوع للملف", callback_data=f"back_to_profile_{user_id}")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    message = f"""👤 إدارة المستخدم

📋 المستخدم: {user_data[2]} {user_data[3]}
🆔 المعرف: {user_id}

⚙️ عمليات الإدارة المتاحة:
• حظر/فك حظر المستخدم
• رفع الحظر المؤقت (بسبب العمليات التخريبية)
• مسح بيانات المستخدم
• إعادة تعيين الإحصائيات

⚠️ تحذير: هذه العمليات لا يمكن التراجع عنها"""
    
    await query.edit_message_text(message, reply_markup=reply_markup)

async def handle_manage_points(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالجة إدارة النقاط"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.data.split("_")[-1]
    user_data = context.user_data.get('selected_user_data')
    
    if not user_data:
        await query.edit_message_text("❌ خطأ: بيانات المستخدم غير متوفرة")
        return
    
    # user_data structure: [0]=user_id, [1]=username, [2]=first_name, [3]=last_name, 
    # [4]=language, [5]=referral_balance, [6]=credits_balance, [7]=referred_by, [8]=join_date, [9]=is_admin
    current_balance = float(user_data[6]) if user_data[6] else 0.0
    
    keyboard = [
        [
            InlineKeyboardButton("➕ إضافة نقاط", callback_data=f"add_points_{user_id}"),
            InlineKeyboardButton("➖ خصم نقاط", callback_data=f"subtract_points_{user_id}")
        ],
        [
            InlineKeyboardButton("🗑️ تصفير الرصيد", callback_data=f"reset_balance_{user_id}"),
            InlineKeyboardButton("💰 تعديل مخصص", callback_data=f"custom_balance_{user_id}")
        ],
        [
            InlineKeyboardButton("📊 سجل المعاملات", callback_data=f"transaction_history_{user_id}")
        ],
        [
            InlineKeyboardButton("🔙 رجوع للملف", callback_data=f"back_to_profile_{user_id}")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    # استخدام نص بسيط بدون Markdown لتجنب أخطاء parsing
    message = f"""💰 إدارة النقاط

📋 المستخدم: {user_data[2]} {user_data[3]}
🆔 المعرف: {user_id}
💳 الرصيد الحالي: ${current_balance:.2f}

⚠️ تنبيه مهم: جميع القيم تُدخل بالنقاط وليس بالدولار!

⚙️ عمليات إدارة النقاط:
• إضافة أو خصم نقاط مع رسائل مخصصة
• تصفير الرصيد بالكامل
• تعديل الرصيد لقيمة مخصصة
• عرض سجل المعاملات

💬 الرسائل: يمكنك اختيار رسالة مخصصة أو قالب جاهز"""
    
    await query.edit_message_text(message, reply_markup=reply_markup)

async def handle_broadcast_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالجة البث للمستخدم المحدد"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.data.split("_")[-1]
    user_data = context.user_data.get('selected_user_data')
    
    if not user_data:
        await query.edit_message_text("❌ خطأ: بيانات المستخدم غير متوفرة")
        return
    
    keyboard = [
        [
            InlineKeyboardButton("📝 رسالة نصية", callback_data=f"send_text_{user_id}"),
            InlineKeyboardButton("🖼️ رسالة مع صورة", callback_data=f"send_photo_{user_id}")
        ],
        [
            InlineKeyboardButton("⚡ رسالة سريعة", callback_data=f"quick_message_{user_id}"),
            InlineKeyboardButton("📢 إشعار هام", callback_data=f"important_notice_{user_id}")
        ],
        [
            InlineKeyboardButton("🔙 رجوع للملف", callback_data=f"back_to_profile_{user_id}")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    message = f"""📢 **بث رسالة للمستخدم**

📋 **المستخدم:** {user_data[2]} {user_data[3]}
🆔 **المعرف:** `{user_id}`
📱 **اسم المستخدم:** @{user_data[1] or 'غير محدد'}

📤 **أنواع الرسائل المتاحة:**
• رسالة نصية عادية
• رسالة مع صورة مرفقة
• رسالة سريعة (قوالب جاهزة)
• إشعار هام (عالي الأولوية)"""
    
    await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')

async def handle_manage_referrals(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالجة إدارة الإحالات"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.data.split("_")[-1]
    user_data = context.user_data.get('selected_user_data')
    
    if not user_data:
        await query.edit_message_text("❌ خطأ: بيانات المستخدم غير متوفرة")
        return
    
    # الحصول على إحصائيات الإحالات
    referral_count = db.execute_query(
        "SELECT COUNT(*) FROM referrals WHERE referrer_id = ?", (user_id,)
    )[0][0]
    
    referral_earnings = float(user_data[5]) if user_data[5] else 0.0
    
    keyboard = [
        [
            InlineKeyboardButton("👥 عرض المُحالين", callback_data=f"show_referred_{user_id}"),
            InlineKeyboardButton("💰 سجل الأرباح", callback_data=f"referral_earnings_{user_id}")
        ],
        [
            InlineKeyboardButton("➕ إدراج إحالة", callback_data=f"add_referral_{user_id}"),
            InlineKeyboardButton("❌ حذف إحالة", callback_data=f"delete_referral_{user_id}")
        ],
        [
            InlineKeyboardButton("🗑️ تصفير رصيد الإحالة", callback_data=f"reset_referral_balance_{user_id}"),
            InlineKeyboardButton("🔄 مسح جميع الإحالات", callback_data=f"clear_referrals_{user_id}")
        ],
        [
            InlineKeyboardButton("🔙 رجوع للملف", callback_data=f"back_to_profile_{user_id}")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    message = f"""👥 **إدارة الإحالات**

📋 **المستخدم:** {user_data[2]} {user_data[3]}
🆔 **المعرف:** `{user_id}`

📊 **إحصائيات الإحالات:**
• عدد المُحالين: `{referral_count}` شخص
• إجمالي الأرباح: `${referral_earnings:.2f}`

⚙️ **عمليات إدارة الإحالات:**
• عرض قائمة المستخدمين المُحالين
• عرض سجل أرباح الإحالات
• إدراج إحالة جديدة يدوياً
• حذف إحالة محددة (مع عرض أسماء المحالين)
• تصفير رصيد الإحالة فقط
• مسح جميع الإحالات"""
    
    await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')

async def handle_detailed_reports(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالجة التقارير المفصلة"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.data.split("_")[-1]
    user_data = context.user_data.get('selected_user_data')
    
    if not user_data:
        await query.edit_message_text("❌ خطأ: بيانات المستخدم غير متوفرة")
        return
    
    keyboard = [
        [
            InlineKeyboardButton("📊 تقرير شامل", callback_data=f"full_report_{user_id}"),
            InlineKeyboardButton("💰 تقرير مالي", callback_data=f"financial_report_{user_id}")
        ],
        [
            InlineKeyboardButton("📦 تقرير الطلبات", callback_data=f"orders_report_{user_id}"),
            InlineKeyboardButton("👥 تقرير الإحالات", callback_data=f"referrals_report_{user_id}")
        ],
        [
            InlineKeyboardButton("📈 إحصائيات متقدمة", callback_data=f"advanced_stats_{user_id}"),
            InlineKeyboardButton("📅 تقرير زمني", callback_data=f"timeline_report_{user_id}")
        ],
        [
            InlineKeyboardButton("🔙 رجوع للملف", callback_data=f"back_to_profile_{user_id}")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    message = f"""📊 **التقارير المفصلة**

📋 **المستخدم:** {user_data[2]} {user_data[3]}
🆔 **المعرف:** `{user_id}`

📈 **أنواع التقارير المتاحة:**
• تقرير شامل لجميع البيانات
• تقرير مالي (رصيد، معاملات، إنفاق)
• تقرير الطلبات (تفصيلي حسب النوع والحالة)
• تقرير الإحالات والأرباح
• إحصائيات متقدمة ورسوم بيانية
• تقرير زمني لنشاط المستخدم"""
    
    await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')

async def handle_user_lookup_unified(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """معالج موحد للبحث عن المستخدمين وتصفير الرصيد"""
    # التحقق من السياق لتحديد العملية المطلوبة
    user_data_action = context.user_data.get('lookup_action', 'lookup')
    
    if user_data_action == 'reset_balance':
        return await handle_balance_reset(update, context)
    else:
        return await handle_user_lookup(update, context)

async def handle_admin_orders_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالجة قائمة إدارة الطلبات للأدمن"""
    keyboard = [
        [KeyboardButton("📋 الطلبات المعلقة")],
        [KeyboardButton("🔍 الاستعلام عن طلب")],
        [KeyboardButton("🗑️ حذف الطلبات المعالجة"), KeyboardButton("🗑️ حذف جميع الطلبات")],
        [KeyboardButton("🔙 العودة للقائمة الرئيسية")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        "📋 إدارة الطلبات\nاختر العملية المطلوبة:",
        reply_markup=reply_markup
    )

async def handle_admin_money_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالجة قائمة إدارة الأموال للأدمن"""
    keyboard = [
        [KeyboardButton("📊 إحصاء المبيعات")],
        [KeyboardButton("💲 إدارة الأسعار")],
        [KeyboardButton("🔙 العودة للقائمة الرئيسية")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        "💰 إدارة الأموال\nاختر العملية المطلوبة:",
        reply_markup=reply_markup
    )

async def handle_admin_referrals_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالجة قائمة إدارة الإحالات للأدمن"""
    keyboard = [
        [KeyboardButton("💵 تحديد قيمة الإحالة")],
        [KeyboardButton("📊 إحصائيات المستخدمين")],
        [KeyboardButton("🗑️ تصفير رصيد مستخدم")],
        [KeyboardButton("🔙 العودة للقائمة الرئيسية")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        "👥 إدارة الإحالات\nاختر العملية المطلوبة:",
        reply_markup=reply_markup
    )

async def handle_admin_settings_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالجة قائمة إعدادات الأدمن"""
    keyboard = [
        [KeyboardButton("🌐 تغيير اللغة")],
        [KeyboardButton("🔐 تغيير كلمة المرور")],
        [KeyboardButton("🔕 ساعات الهدوء")],
        [KeyboardButton("📝 تعديل رسالة الخدمات")],
        [KeyboardButton("💱 تعديل رسالة سعر الصرف")],
        [KeyboardButton("🗃️ إدارة قاعدة البيانات")],
        [KeyboardButton("🔙 العودة للقائمة الرئيسية")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        "⚙️ إعدادات الأدمن\nاختر العملية المطلوبة:",
        reply_markup=reply_markup
    )

async def handle_admin_user_lookup(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """معالجة استعلام عن مستخدم"""
    keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data="cancel_user_lookup")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "🔍 استعلام عن مستخدم\n\nيرجى إرسال:\n- معرف المستخدم (رقم)\n- أو اسم المستخدم (@username)",
        reply_markup=reply_markup
    )
    return USER_LOOKUP

async def return_to_user_mode(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """العودة لوضع المستخدم العادي"""
    context.user_data['is_admin'] = False
    user_id = update.effective_user.id
    language = get_user_language(user_id)
    
    # إنشاء الأزرار الرئيسية للمستخدم
    keyboard = [
        [KeyboardButton(MESSAGES[language]['main_menu_buttons'][0])],
        [KeyboardButton(MESSAGES[language]['main_menu_buttons'][1])],
        [KeyboardButton(MESSAGES[language]['main_menu_buttons'][2]), 
         KeyboardButton(MESSAGES[language]['main_menu_buttons'][3])]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        MESSAGES[language]['welcome'],
        reply_markup=reply_markup
    )

async def show_pending_orders_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """عرض الطلبات المعلقة للأدمن مع إمكانية اختيار الطلب لعرض التفاصيل"""
    try:
        pending_orders = db.get_pending_orders()
        
        if not pending_orders:
            await update.message.reply_text("✅ لا توجد طلبات معلقة حالياً.")
            return
        
        total_orders = len(pending_orders)
        
        await update.message.reply_text(f"📋 **الطلبات المعلقة** - المجموع: {total_orders} طلب\n\n🔽 اختر طلباً لعرض تفاصيله الكاملة مع إثبات الدفع:", parse_mode='Markdown')
        
        # إنشاء أزرار لعرض تفاصيل كل طلب
        keyboard = []
        for i, order in enumerate(pending_orders[:20], 1):  # عرض أول 20 طلب لتجنب تجاوز حدود التيليجرام
            try:
                # التحقق من صحة بيانات الطلب قبل المعالجة
                order_id = str(order[0]) if order[0] else "unknown"
                proxy_type = str(order[2]) if len(order) > 2 and order[2] else "unknown"
                amount = str(order[6]) if len(order) > 6 and order[6] else "0"
                
                # عرض معلومات مختصرة في النص
                button_text = f"{i}. {order_id[:8]}... ({proxy_type} - {amount}$)"
                keyboard.append([InlineKeyboardButton(button_text, callback_data=f"view_pending_order_{order_id}")])
            except Exception as order_error:
                logger.error(f"Error processing pending order {i}: {order_error}")
                # إضافة زر للطلب التالف مع معلومات أساسية
                keyboard.append([InlineKeyboardButton(f"{i}. طلب تالف - إصلاح مطلوب", callback_data=f"fix_order_{i}")])
        
        # إضافة زر لعرض المزيد إذا كان هناك أكثر من 20 طلب
        if total_orders > 20:
            keyboard.append([InlineKeyboardButton(f"عرض المزيد... ({total_orders - 20} طلب إضافي)", callback_data="show_more_pending")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("📋 **قائمة الطلبات المعلقة:**", parse_mode='Markdown', reply_markup=reply_markup)
        
    except Exception as e:
        logger.error(f"Error in show_pending_orders_admin: {e}")
        print(f"❌ خطأ في عرض الطلبات المعلقة: {e}")
        
        # إرسال رسالة خطأ للأدمن مع خيارات
        try:
            # التحقق من صحة البيانات المطلوبة
            if not update or not hasattr(update, 'message') or not update.message:
                raise Exception("Update or message object is invalid")
                
            keyboard = [
                [InlineKeyboardButton("🔄 إعادة المحاولة", callback_data="retry_pending_orders")],
                [InlineKeyboardButton("🗃️ إدارة قاعدة البيانات", callback_data="admin_database_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                "❌ حدث خطأ في تحميل الطلبات المعلقة\n\n"
                "قد يكون السبب:\n"
                "• مشكلة في قاعدة البيانات\n"
                "• بيانات تالفة في الطلبات\n"
                "• نفاد الذاكرة\n\n"
                "الرجاء اختيار إجراء:",
                reply_markup=reply_markup
            )
        except Exception as msg_error:
            logger.error(f"Failed to send error message: {msg_error}")
            # محاولة إرسال رسالة بسيطة بدون أزرار
            try:
                await update.message.reply_text("❌ حدث خطأ في تحميل الطلبات المعلقة")
                await asyncio.sleep(2)
                await restore_admin_keyboard(context, update.effective_chat.id)
            except Exception as final_error:
                logger.error(f"Final fallback failed in show_pending_orders: {final_error}")
                # العودة للوحة الأدمن الرئيسية كحل أخير
                await restore_admin_keyboard(context, update.effective_chat.id, "❌ حدث خطأ في النظام. تم إعادة تعيين الواجهة.")

async def delete_processed_orders(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """حذف الطلبات المعالجة (المكتملة والفاشلة)"""
    # عد الطلبات المعالجة (المكتملة والفاشلة)
    count_query = """
        SELECT COUNT(*) FROM orders 
        WHERE status IN ('completed', 'failed')
    """
    count_result = db.execute_query(count_query, ())
    count_before = count_result[0][0] if count_result else 0
    
    # عد الطلبات المكتملة والفاشلة بشكل منفصل للتقرير
    completed_count = db.execute_query("SELECT COUNT(*) FROM orders WHERE status = 'completed'")[0][0] if db.execute_query("SELECT COUNT(*) FROM orders WHERE status = 'completed'") else 0
    failed_count = db.execute_query("SELECT COUNT(*) FROM orders WHERE status = 'failed'")[0][0] if db.execute_query("SELECT COUNT(*) FROM orders WHERE status = 'failed'") else 0
    
    # حذف الطلبات المعالجة (المكتملة والفاشلة)
    delete_query = """
        DELETE FROM orders 
        WHERE status IN ('completed', 'failed')
    """
    db.execute_query(delete_query, ())
    
    await update.message.reply_text(
        f"🗑️ تم حذف {count_before} طلب معالج:\n\n"
        f"✅ طلبات مكتملة: {completed_count}\n"
        f"❌ طلبات فاشلة: {failed_count}\n\n"
        f"📋 تم الاحتفاظ بالطلبات المعلقة."
    )

async def delete_all_orders(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """حذف جميع الطلبات مع رسالة تأكيد"""
    user_id = update.effective_user.id
    
    # عرض رسالة التأكيد
    # عد جميع الطلبات بحسب الحالة
    pending_count = db.execute_query("SELECT COUNT(*) FROM orders WHERE status = 'pending'")[0][0] if db.execute_query("SELECT COUNT(*) FROM orders WHERE status = 'pending'") else 0
    completed_count = db.execute_query("SELECT COUNT(*) FROM orders WHERE status = 'completed'")[0][0] if db.execute_query("SELECT COUNT(*) FROM orders WHERE status = 'completed'") else 0
    failed_count = db.execute_query("SELECT COUNT(*) FROM orders WHERE status = 'failed'")[0][0] if db.execute_query("SELECT COUNT(*) FROM orders WHERE status = 'failed'") else 0
    total_count = pending_count + completed_count + failed_count
    
    # حفظ معرف الأدمن للتأكيد
    context.user_data['delete_all_orders_user_id'] = user_id
    context.user_data['delete_all_orders_counts'] = {
        'pending': pending_count,
        'completed': completed_count, 
        'failed': failed_count,
        'total': total_count
    }
    
    confirmation_message = f"""⚠️ **تحذير: حذف جميع الطلبات**

هل أنت متأكد من حذف **جميع الطلبات** من قاعدة البيانات؟

📊 **إحصائيات الطلبات الحالية:**
⏳ طلبات معلقة: {pending_count}
✅ طلبات مكتملة: {completed_count}
❌ طلبات فاشلة: {failed_count}
📋 **المجموع الكلي: {total_count} طلب**

🚨 **تحذير:** هذا الإجراء غير قابل للتراجع!

أكتب "نعم أحذف الجميع" للتأكيد أو أي شيء آخر للإلغاء."""
    
    await update.message.reply_text(confirmation_message, parse_mode='Markdown')
    
    return CONFIRM_DELETE_ALL_ORDERS

async def handle_confirm_delete_all_orders(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """معالجة تأكيد حذف جميع الطلبات"""
    user_text = update.message.text.strip()
    
    if user_text == "نعم أحذف الجميع":
        # تنفيذ حذف جميع الطلبات
        counts = context.user_data.get('delete_all_orders_counts', {})
        
        # حذف جميع الطلبات
        db.execute_query("DELETE FROM orders", ())
        
        # إرسال تقرير الحذف
        report_message = f"""✅ **تم حذف جميع الطلبات بنجاح**

📊 **تقرير الحذف:**
⏳ طلبات معلقة محذوفة: {counts.get('pending', 0)}
✅ طلبات مكتملة محذوفة: {counts.get('completed', 0)}
❌ طلبات فاشلة محذوفة: {counts.get('failed', 0)}

🗑️ **المجموع المحذوف: {counts.get('total', 0)} طلب**

📋 قاعدة البيانات الآن خالية من جميع الطلبات."""

        await update.message.reply_text(report_message, parse_mode='Markdown')
        
        # تنظيف البيانات المؤقتة
        context.user_data.pop('delete_all_orders_user_id', None)
        context.user_data.pop('delete_all_orders_counts', None)
        
        # العودة للوحة الأدمن
        await restore_admin_keyboard(context, update.effective_chat.id, "🔧 لوحة الأدمن جاهزة")
        
    else:
        # إلغاء العملية
        await update.message.reply_text("❌ تم إلغاء عملية حذف جميع الطلبات.\n\n✅ لم يتم حذف أي طلب.")
        
        # تنظيف البيانات المؤقتة
        context.user_data.pop('delete_all_orders_user_id', None)
        context.user_data.pop('delete_all_orders_counts', None)
        
        # العودة للوحة الأدمن
        await restore_admin_keyboard(context, update.effective_chat.id, "🔧 لوحة الأدمن جاهزة")
    
    return ConversationHandler.END

async def show_sales_statistics(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """عرض إحصائيات المبيعات"""
    # إحصائيات المبيعات الناجحة
    stats = db.execute_query("""
        SELECT COUNT(*), SUM(payment_amount) 
        FROM orders 
        WHERE status = 'completed' AND proxy_type != 'withdrawal'
    """)[0]
    
    # إحصائيات السحوبات
    withdrawals = db.execute_query("""
        SELECT COUNT(*), SUM(payment_amount)
        FROM orders 
        WHERE proxy_type = 'withdrawal' AND status = 'completed'
    """)[0]
    
    total_orders = stats[0] or 0
    total_revenue = stats[1] or 0.0
    withdrawal_count = withdrawals[0] or 0
    withdrawal_amount = withdrawals[1] or 0.0
    
    message = f"""📊 إحصائيات المبيعات

💰 المبيعات الناجحة:
📦 عدد الطلبات: {total_orders}
💵 إجمالي الإيرادات: `{total_revenue:.2f}$`

💸 السحوبات:
📋 عدد الطلبات: {withdrawal_count}
💰 إجمالي المسحوب: `{withdrawal_amount:.2f}$`

━━━━━━━━━━━━━━━
📈 صافي الربح: `{total_revenue - withdrawal_amount:.2f}$`"""
    
    await update.message.reply_text(message, parse_mode='Markdown')

async def database_management_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """قائمة إدارة قاعدة البيانات"""
    keyboard = [
        [KeyboardButton("🔍 فحص قاعدة البيانات")],
        [KeyboardButton("📊 تحميل قاعدة البيانات")],
        [KeyboardButton("🗑️ تفريغ قاعدة البيانات")],
        [KeyboardButton("🔙 العودة للقائمة الرئيسية")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        "🗃️ إدارة قاعدة البيانات\nاختر العملية المطلوبة:",
        reply_markup=reply_markup
    )

async def database_export_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """قائمة تصدير قاعدة البيانات"""
    keyboard = [
        [KeyboardButton("📊 Excel"), KeyboardButton("📄 CSV")],
        [KeyboardButton("🗃️ SQLite Database"), KeyboardButton("🔧 Export Mix")],
        [KeyboardButton("🔙 العودة للقائمة الرئيسية")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        "📊 تحميل قاعدة البيانات\nاختر صيغة التصدير:",
        reply_markup=reply_markup
    )

async def return_to_admin_main(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """العودة للقائمة الرئيسية للأدمن"""
    await restore_admin_keyboard(context, update.effective_chat.id, "🔧 لوحة الأدمن الرئيسية\nاختر الخدمة المطلوبة:")

async def handle_text_messages(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالجة الرسائل النصية"""
    # فحص حالة الحظر وتتبع النقرات المتكررة
    ban_check_result = await check_user_ban_and_track_clicks(update, context)
    if ban_check_result:
        # المستخدم محظور أو تم تطبيق إجراء - إيقاف المعالجة
        return
        
    try:
        text = update.message.text
        user_id = update.effective_user.id
        
        # فحص طول الرسالة لتجنب المشاكل
        if len(text) > 1000:  # رسالة طويلة جداً
            await update.message.reply_text(
                "⚠️ الرسالة طويلة جداً. يرجى إرسال رسالة أقصر.",
                reply_markup=ReplyKeyboardRemove()
            )
            return
        
        # فحص الرسائل المكررة أو المشبوهة
        if len(text) > 10 and text.count(text[0]) > len(text) * 0.8:  # رسالة مكررة
            logger.warning(f"Suspicious repeated message from user {user_id}")
            await update.message.reply_text(
                "⚠️ يرجى عدم إرسال رسائل مكررة.",
                reply_markup=ReplyKeyboardRemove()
            )
            return
        
        language = get_user_language(user_id)
        is_admin = context.user_data.get('is_admin', False)
    except Exception as e:
        logger.error(f"Error in handle_text_messages initialization: {e}")
        try:
            await update.message.reply_text("⚠️ حدث خطأ. استخدم /start لإعادة التشغيل.")
        except:
            pass
        return
    
    try:
        # معالجة إدخال الرصيد المخصص للأدمن
        if is_admin and context.user_data.get('awaiting_custom_balance'):
            await handle_custom_balance_input(update, context)
            return
        
        # التحقق من الأوامر الخاصة للتنظيف وإعادة التعيين
        if text.lower() in ['/reset', '🔄 إعادة تعيين', 'reset']:
            await handle_reset_command(update, context)
            return
        elif text.lower() in ['/cleanup', '🧹 تنظيف', 'cleanup']:
            await handle_cleanup_command(update, context)
            return
        elif text.lower() in ['/status', '📊 الحالة', 'status']:
            await handle_status_command(update, context)
            return
        elif text.lower() in ['إلغاء', 'cancel', 'خروج', 'exit', 'stop']:
            # تنظيف العمليات المعلقة والعودة للقائمة الرئيسية
            is_admin = context.user_data.get('is_admin', False) or user_id in ACTIVE_ADMINS
            clean_user_data_preserve_admin(context)
            
            if is_admin:
                await update.message.reply_text("✅ تم إلغاء العملية")
                await restore_admin_keyboard(context, update.effective_chat.id, "🔄 العودة للقائمة الرئيسية")
            else:
                await update.message.reply_text("✅ تم إلغاء العملية والعودة للقائمة الرئيسية")
                await start(update, context)
            return
        
        # معالجة إدخال كمية البروكسي الستاتيك
        if context.user_data.get('waiting_for_static_quantity'):
            await handle_static_quantity_input(update, context)
            return
        
            
            # الانتقال لطرق الدفع
            if language == 'ar':
                keyboard = [
                    [InlineKeyboardButton("💳 شام كاش", callback_data="payment_shamcash")],
                    [InlineKeyboardButton("💳 سيرياتيل كاش", callback_data="payment_syriatel")],
                    [InlineKeyboardButton("🪙 Coinex", callback_data="payment_coinex")],
                    [InlineKeyboardButton("🪙 Binance", callback_data="payment_binance")],
                    [InlineKeyboardButton("🪙 Payeer", callback_data="payment_payeer")]
                ]
            else:
                keyboard = [
                    [InlineKeyboardButton("💳 Sham Cash", callback_data="payment_shamcash")],
                    [InlineKeyboardButton("💳 Syriatel Cash", callback_data="payment_syriatel")],
                    [InlineKeyboardButton("🪙 Coinex", callback_data="payment_coinex")],
                    [InlineKeyboardButton("🪙 Binance", callback_data="payment_binance")],
                    [InlineKeyboardButton("🪙 Payeer", callback_data="payment_payeer")]
                ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(
                MESSAGES[language]['payment_methods'],
                reply_markup=reply_markup
            )
            return
        
        # التحقق من حالة انتظار رسالة مباشرة من الأدمن (للمعالجة المباشرة)
        if is_admin and context.user_data.get('waiting_for_direct_admin_message'):
            order_id = context.user_data.get('processing_order_id')
            if order_id:
                try:
                    # استدعاء دالة إرسال البروكسي مع الرسالة المخصصة
                    await send_proxy_with_custom_message_direct(update, context, text)
                    
                    # رسالة تأكيد للأدمن
                    await update.message.reply_text(
                        f"✅ تم إرسال البروكسي والرسالة للمستخدم بنجاح!\n\n🆔 معرف الطلب: {order_id}",
                        parse_mode='Markdown'
                    )
                    
                    # إعادة تفعيل كيبورد الأدمن
                    await restore_admin_keyboard(context, update.effective_chat.id)
                    
                except Exception as e:
                    logger.error(f"خطأ في إرسال البروكسي: {e}")
                    await update.message.reply_text(
                        f"❌ حدث خطأ أثناء إرسال البروكسي\n\nالخطأ: {str(e)}"
                    )
                return
        
        # التحقق من حالة انتظار رسالة أدمن عادية
        if is_admin and context.user_data.get('waiting_for_admin_message'):
            try:
                await handle_admin_message_for_proxy(update, context)
                return
            except Exception as e:
                logger.error(f"خطأ في معالجة رسالة الأدمن المخصصة: {e}")
                await update.message.reply_text(
                    f"❌ حدث خطأ أثناء معالجة رسالتك\n\nالخطأ: {str(e)}"
                )
                await restore_admin_keyboard(context, update.effective_chat.id)
                return
        
        # أزرار الأدمن
        if is_admin:
            # القوائم الرئيسية للأدمن
            if text == "📋 إدارة الطلبات":
                await handle_admin_orders_menu(update, context)
            elif text == "💰 إدارة الأموال":
                await handle_admin_money_menu(update, context)
            elif text == "👥 الإحالات":
                await handle_admin_referrals_menu(update, context)
            elif text == "🌐 إدارة البروكسيات":
                await handle_manage_proxies(update, context)
            elif text == "⚙️ الإعدادات":
                await handle_admin_settings_menu(update, context)
            elif text == "🚪 تسجيل الخروج":
                await admin_logout_confirmation(update, context)
            
            # إدارة الطلبات
            elif text == "📋 الطلبات المعلقة":
                await show_pending_orders_admin(update, context)
            elif text == "🔍 الاستعلام عن طلب":
                await admin_order_inquiry(update, context)
            elif text == "🗑️ حذف الطلبات المعالجة":
                await delete_processed_orders(update, context)
            
            # إدارة الأموال
            elif text == "📊 إحصاء المبيعات":
                await show_sales_statistics(update, context)
            elif text == "💲 إدارة الأسعار":
                await manage_prices_menu(update, context)
            elif text == "💰 تعديل سعر النقطة":
                await set_credit_price(update, context)
            elif text == "💰 تعديل أسعار ستاتيك":
                await manage_static_prices_menu(update, context)
            elif text == "💰 تعديل أسعار سوكس":
                await set_socks_prices(update, context)
            elif text == "🔙 رجوع" and context.user_data.get('last_admin_action') == 'socks_price_menu':
                await manage_prices_menu(update, context)
                context.user_data.pop('last_admin_action', None)
            elif text == "💰 Res1":
                await set_res1_prices(update, context)
            elif text == "💰 Res2":
                await set_res2_prices(update, context)
            elif text == "💰 Isp":
                await set_isp_prices(update, context)
            elif text == "💰 Datacenter":
                await set_datacenter_prices(update, context)
            elif text == "💰 Daily":
                await set_daily_prices(update, context)
            elif text == "💰 Weekly":
                await set_weekly_prices(update, context)
            elif text == "🔙 العودة لإدارة الأسعار":
                await manage_prices_menu(update, context)
            
            # إدارة الإحالات
            elif text == "💵 تحديد قيمة الإحالة":
                await set_referral_amount(update, context)
            elif text == "📊 إحصائيات المستخدمين":
                await show_user_statistics(update, context)
            elif text == "🗑️ تصفير رصيد مستخدم":
                await reset_user_balance(update, context)
            
            # إعدادات الأدمن
            elif text == "🌐 تغيير اللغة":
                await handle_settings(update, context)
            elif text == "🔐 تغيير كلمة المرور":
                await change_admin_password(update, context)
            elif text == "🔕 ساعات الهدوء":
                await set_quiet_hours(update, context)
            elif text == "🗃️ إدارة قاعدة البيانات":
                await database_management_menu(update, context)
            
            # معالجة إدارة قاعدة البيانات
            elif text == "📊 تحميل قاعدة البيانات":
                await database_export_menu(update, context)
            elif text == "🗑️ تفريغ قاعدة البيانات":
                await confirm_database_clear(update, context)
            
            # معالجة تصدير قاعدة البيانات
            elif text == "📊 Excel":
                await export_database_excel(update, context)
            elif text == "📄 CSV":
                await export_database_csv(update, context)
            elif text == "🗃️ SQLite Database":
                await export_database_sqlite(update, context)
            elif text == "🔧 Export Mix":
                await export_database_json_mix(update, context)
            
            # العودة للقائمة الرئيسية
            elif text == "🔙 العودة للقائمة الرئيسية":
                await restore_admin_keyboard(context, update.effective_chat.id, "🔧 لوحة الأدمن الرئيسية\nاختر الخدمة المطلوبة:")
            
            # إذا وصلنا هنا فالنص لا يتطابق مع أي زر أدمن معروف
            # لا نفعل شيئاً - تماماً كما في proxy_bot.py
            return
        
        # التحقق من الأزرار الرئيسية للمستخدم
        if text == MESSAGES[language]['main_menu_buttons'][0]:  # طلب بروكسي ستاتيك
            await handle_static_proxy_request(update, context)
            return
        elif text == MESSAGES[language]['main_menu_buttons'][1]:  # طلب بروكسي سوكس
            await handle_socks_proxy_request(update, context)
            return
        elif text == MESSAGES[language]['main_menu_buttons'][2]:  # تجربة ستاتيك مجانا
            await handle_free_static_trial(update, context)
            return
        elif text == MESSAGES[language]['main_menu_buttons'][3]:  # الرصيد
            await handle_balance_menu(update, context)
            return
        elif text == MESSAGES[language]['main_menu_buttons'][4]:  # تذكير بطلباتي
            await handle_order_reminder(update, context)
            return
        elif text == MESSAGES[language]['main_menu_buttons'][5]:  # الإعدادات
            await handle_settings(update, context)
            return
        elif text == MESSAGES[language]['main_menu_buttons'][6]:  # خدماتنا
            await handle_services(update, context)
            return
        
        # معالجة أزرار قائمة الرصيد الفرعية
        if text == MESSAGES[language]['balance_menu_buttons'][0]:  # شحن رصيد
            await handle_recharge_balance(update, context)
            return
        elif text == MESSAGES[language]['balance_menu_buttons'][1]:  # رصيدي  
            await handle_my_balance(update, context)
            return
        elif text == MESSAGES[language]['balance_menu_buttons'][2]:  # الإحالات
            await handle_balance_referrals(update, context)
            return
        elif text == MESSAGES[language]['balance_menu_buttons'][3]:  # العودة للقائمة الرئيسية
            await handle_back_to_main_menu(update, context)
            return
        
        # معالجة إدخال مبلغ الشحن
        if context.user_data.get('waiting_for_recharge_amount'):
            await handle_recharge_amount_input(update, context)
            return
        
        # معالجة إثبات دفع الشحن
        if context.user_data.get('waiting_for_recharge_proof'):
            await handle_recharge_payment_proof(update, context)
            return
        
        # معالجة أزرار الأدمن
        if is_admin:
            if text == "📝 تعديل رسالة الخدمات":
                await handle_edit_services_message(update, context)
                return
            
            if text == "💱 تعديل رسالة سعر الصرف":
                await handle_edit_exchange_rate_message(update, context)
                return
                
        # إذا وصلنا هنا فالنص لا يتطابق مع أي زر معروف
        # لا نفعل شيئاً - تماماً كما في proxy_bot.py
        
    except Exception as e:
        logger.error(f"Error in handle_text_messages: {e}")
        print(f"❌ خطأ في معالجة رسالة نصية من المستخدم {user_id}: {e}")
        print(f"   النص: {text}")
        
        # معالجة الخطأ فقط في حالة حدوث استثناء حقيقي
        try:
            user_id = update.effective_user.id
            language = get_user_language(user_id)
            
            if context.user_data.get('is_admin') or user_id in ACTIVE_ADMINS:
                error_details = f"❌ حدث خطأ في معالجة الرسالة النصية\n\n🔍 التفاصيل التقنية:\n• النص المُرسل: {text[:100]}...\n• سبب الخطأ: {str(e)[:200]}...\n\n🔧 تم إعادة توجيهك للقائمة الرئيسية"
                await restore_admin_keyboard(context, update.effective_chat.id, error_details)
            else:
                # إنشاء الكيبورد من جديد بدلاً من إزالته
                keyboard = [
                    [KeyboardButton(MESSAGES[language]['main_menu_buttons'][0])],  # طلب بروكسي ستاتيك
                    [KeyboardButton(MESSAGES[language]['main_menu_buttons'][1])],  # طلب بروكسي سوكس
                    [KeyboardButton(MESSAGES[language]['main_menu_buttons'][2]), KeyboardButton(MESSAGES[language]['main_menu_buttons'][3])],  # تجربة ستاتيك + الرصيد
                    [KeyboardButton(MESSAGES[language]['main_menu_buttons'][5]), KeyboardButton(MESSAGES[language]['main_menu_buttons'][4])],  # الإعدادات + تذكير بطلباتي
                    [KeyboardButton(MESSAGES[language]['main_menu_buttons'][6])]  # المزيد من الخدمات
                ]
                reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
                
                if language == 'ar':
                    await update.message.reply_text(
                        "❌ حدث خطأ في معالجة طلبك.\n\n🔄 تم إعادة إنشاء الأزرار. يرجى المحاولة مرة أخرى:",
                        reply_markup=reply_markup
                    )
                else:
                    await update.message.reply_text(
                        "❌ An error occurred while processing your request.\n\n🔄 Buttons have been recreated. Please try again:",
                        reply_markup=reply_markup
                    )
        except Exception as redirect_error:
            logger.error(f"Failed to redirect user after text message error: {redirect_error}")
            # محاولة أخيرة بسيطة
            try:
                await context.bot.send_message(
                    user_id,
                    "❌ حدث خطأ. يرجى استخدام /start لإعادة تشغيل البوت"
                )
            except:
                pass
        
        # تنظيف البيانات المؤقتة في حالة الخطأ فقط
        try:
            clean_user_data_preserve_admin(context)
        except:
            pass

async def handle_photo_messages(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالجة الصور المرسلة من المستخدمين"""
    # فحص حالة الحظر وتتبع النقرات المتكررة
    ban_check_result = await check_user_ban_and_track_clicks(update, context)
    if ban_check_result:
        # المستخدم محظور أو تم تطبيق إجراء - إيقاف المعالجة
        return
    
    try:
        user_id = update.effective_user.id
        language = get_user_language(user_id)
        
        # معالجة إثبات دفع الشحن
        if context.user_data.get('waiting_for_recharge_proof'):
            await handle_recharge_payment_proof(update, context)
            return
        
        # معالجة إثبات الدفع العادي
        if context.user_data.get('waiting_for_payment_proof'):
            # تطبيق المنطق الموجود في handle_text_messages للصور
            file_id = update.message.photo[-1].file_id
            context.user_data['payment_proof'] = f"photo:{file_id}"
            
            # متابعة المعالجة العادية كما في handle_text_messages
            await handle_payment_proof_processing(update, context)
            return
        
        # إذا لم تكن هناك حالة انتظار محددة، إرسال رسالة توضيحية
        if language == 'ar':
            await update.message.reply_text("📷 تم استلام الصورة. إذا كنت تريد إرسال إثبات دفع، يرجى اختيار الخدمة أولاً.")
        else:
            await update.message.reply_text("📷 Image received. If you want to send payment proof, please select the service first.")
            
    except Exception as e:
        logger.error(f"Error in handle_photo_messages: {e}")
        print(f"❌ خطأ في معالجة صورة من المستخدم {user_id}: {e}")

async def handle_document_messages(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالجة المستندات المرسلة من المستخدمين"""
    # فحص حالة الحظر وتتبع النقرات المتكررة
    ban_check_result = await check_user_ban_and_track_clicks(update, context)
    if ban_check_result:
        # المستخدم محظور أو تم تطبيق إجراء - إيقاف المعالجة
        return
    
    try:
        user_id = update.effective_user.id
        language = get_user_language(user_id)
        
        # إرسال رسالة توضيحية للمستندات
        if language == 'ar':
            await update.message.reply_text("📄 تم استلام المستند. لإثبات الدفع، يرجى إرسال صورة بدلاً من مستند.")
        else:
            await update.message.reply_text("📄 Document received. For payment proof, please send an image instead of a document.")
            
    except Exception as e:
        logger.error(f"Error in handle_document_messages: {e}")
        print(f"❌ خطأ في معالجة مستند من المستخدم {user_id}: {e}")

async def validate_database_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """عرض تقرير فحص سلامة قاعدة البيانات"""
    try:
        # إجراء فحص سلامة قاعدة البيانات
        validation_results = db.validate_database_integrity()
        
        # تكوين الرسالة
        status_icon = "✅" if all([
            validation_results['database_accessible'],
            validation_results['tables_exist'], 
            validation_results['data_integrity']
        ]) else "❌"
        
        message = f"""{status_icon} **تقرير فحص قاعدة البيانات**

🔍 **حالة قاعدة البيانات:**
{"✅" if validation_results['database_accessible'] else "❌"} إمكانية الوصول: {"متاحة" if validation_results['database_accessible'] else "غير متاحة"}
{"✅" if validation_results['tables_exist'] else "❌"} الجداول: {"موجودة" if validation_results['tables_exist'] else "مفقودة"}
{"✅" if validation_results['data_integrity'] else "❌"} سلامة البيانات: {"سليمة" if validation_results['data_integrity'] else "تالفة"}

"""
        
        if validation_results['errors']:
            message += f"⚠️ **الأخطاء المكتشفة:**\n"
            for i, error in enumerate(validation_results['errors'][:5], 1):  # عرض أول 5 أخطاء
                message += f"{i}. {error}\n"
            
            if len(validation_results['errors']) > 5:
                message += f"... و {len(validation_results['errors']) - 5} خطأ إضافي\n"
        else:
            message += "🎉 **لا توجد أخطاء!** قاعدة البيانات تعمل بشكل طبيعي"
        
        message += f"\n📊 **إحصائيات سريعة:**"
        
        try:
            # إحصائيات سريعة
            stats = {
                'users': db.execute_query("SELECT COUNT(*) FROM users"),
                'orders': db.execute_query("SELECT COUNT(*) FROM orders"),
                'pending_orders': db.execute_query("SELECT COUNT(*) FROM orders WHERE status = 'pending'")
            }
            
            message += f"""
👥 المستخدمين: {stats['users'][0][0] if stats['users'] else 'غير معروف'}
📦 إجمالي الطلبات: {stats['orders'][0][0] if stats['orders'] else 'غير معروف'}
⏳ الطلبات المعلقة: {stats['pending_orders'][0][0] if stats['pending_orders'] else 'غير معروف'}"""
        except:
            message += "\n⚠️ تعذر الحصول على الإحصائيات"
        
        # إنشاء أزرار الإجراءات
        keyboard = []
        
        if not all([validation_results['database_accessible'], validation_results['tables_exist']]):
            keyboard.append([InlineKeyboardButton("🔧 إصلاح قاعدة البيانات", callback_data="repair_database")])
        
        keyboard.extend([
            [InlineKeyboardButton("🔄 إعادة الفحص", callback_data="validate_database")],
            [InlineKeyboardButton("📊 تحميل قاعدة البيانات", callback_data="admin_db_export")],
            [InlineKeyboardButton("🔙 العودة", callback_data="admin_database_menu")]
        ])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if hasattr(update, 'callback_query') and update.callback_query:
            await update.callback_query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')
        else:
            await update.message.reply_text(message, reply_markup=reply_markup, parse_mode='Markdown')
            
    except Exception as e:
        error_message = f"""❌ **فشل فحص قاعدة البيانات**

حدث خطأ أثناء محاولة فحص قاعدة البيانات:
`{str(e)}`

هذا قد يشير إلى مشكلة خطيرة في النظام."""
        
        keyboard = [
            [InlineKeyboardButton("🔄 إعادة المحاولة", callback_data="validate_database")],
            [InlineKeyboardButton("🔙 العودة", callback_data="admin_database_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if hasattr(update, 'callback_query') and update.callback_query:
            await update.callback_query.edit_message_text(error_message, reply_markup=reply_markup, parse_mode='Markdown')
        else:
            await update.message.reply_text(error_message, reply_markup=reply_markup, parse_mode='Markdown')

# ==== الوظائف المفقودة ====

async def manage_prices_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """قائمة إدارة الأسعار"""
    keyboard = [
        [KeyboardButton("💰 تعديل سعر النقطة")],
        [KeyboardButton("💰 تعديل أسعار ستاتيك")],
        [KeyboardButton("💰 تعديل أسعار سوكس")],
        [KeyboardButton("🔙 العودة للقائمة الرئيسية")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        "💲 إدارة الأسعار\nاختر نوع البروكسي لتعديل أسعاره:",
        reply_markup=reply_markup
    )

async def manage_static_prices_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """قائمة إدارة أسعار الستاتيك"""
    keyboard = [
        [KeyboardButton("💰 Res1")],
        [KeyboardButton("💰 Res2")],
        [KeyboardButton("💰 Isp")],
        [KeyboardButton("💰 Datacenter")],
        [KeyboardButton("💰 Daily")],
        [KeyboardButton("💰 Weekly")],
        [KeyboardButton("🔙 العودة لإدارة الأسعار")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        "💲 إدارة أسعار الستاتيك\nاختر النوع المطلوب تعديل سعره:",
        reply_markup=reply_markup
    )

async def set_referral_amount(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """تحديد نسبة الإحالة المئوية"""
    keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data="cancel_referral_amount")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "💵 تحديد نسبة الإحالة المئوية\n\nيرجى إرسال النسبة المئوية (مثال: `10` للحصول على 10%):",
        parse_mode='Markdown',
        reply_markup=reply_markup
    )
    return REFERRAL_AMOUNT

async def handle_referral_amount_update(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """معالجة تحديث نسبة الإحالة المئوية"""

    
    try:
        percentage = float(update.message.text)
        
        # التحقق من أن النسبة بين 0 و 100
        if percentage < 0 or percentage > 100:
            keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data="cancel_referral_amount")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text("❌ يرجى إرسال نسبة بين 0 و 100!", reply_markup=reply_markup)
            return REFERRAL_AMOUNT
        
        # حفظ في قاعدة البيانات
        db.execute_query(
            "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
            ("referral_percentage", str(percentage))
        )
        
        await update.message.reply_text(f"✅ تم تحديث نسبة الإحالة إلى {percentage}%\n\n📢 سيتم إشعار جميع المستخدمين بالتحديث...", parse_mode='Markdown')
        
        # إشعار جميع المستخدمين بالتحديث
        await broadcast_referral_update(context, percentage)
        
        # إعادة تفعيل كيبورد الأدمن الرئيسي
        await restore_admin_keyboard(context, update.effective_chat.id, f"✅ تم تحديث نسبة الإحالة إلى {percentage}% بنجاح")
        
    except ValueError:
        keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data="cancel_referral_amount")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("❌ يرجى إرسال رقم صحيح للنسبة المئوية!", reply_markup=reply_markup)
        return REFERRAL_AMOUNT
    
    return ConversationHandler.END

async def set_credit_price(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """تحديد سعر النقطة الواحدة"""
    keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data="cancel_credit_price")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "💰 تعديل سعر النقطة الواحدة\n\nيرجى إرسال السعر الجديد للنقطة الواحدة (مثال: `0.1`):",
        parse_mode='Markdown',
        reply_markup=reply_markup
    )
    return SET_POINT_PRICE

async def handle_credit_price_update(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """معالجة تحديث سعر النقطة الواحدة"""
    
    try:
        price = float(update.message.text)
        
        # التحقق من أن السعر إيجابي
        if price <= 0:
            keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data="cancel_credit_price")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text("❌ يرجى إرسال سعر إيجابي!", reply_markup=reply_markup)
            return SET_POINT_PRICE
        
        # حفظ في قاعدة البيانات
        db.execute_query(
            "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
            ("credit_price", str(price))
        )
        
        await update.message.reply_text(f"✅ تم تحديث سعر النقطة الواحدة إلى ${price}", parse_mode='Markdown')
        
        # إعادة تفعيل كيبورد الأدمن الرئيسي
        await restore_admin_keyboard(context, update.effective_chat.id, f"✅ تم تحديث سعر النقطة الواحدة إلى ${price} بنجاح")
        
    except ValueError:
        keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data="cancel_credit_price")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("❌ يرجى إرسال رقم صحيح للسعر!", reply_markup=reply_markup)
        return SET_POINT_PRICE
    
    return ConversationHandler.END

async def set_quiet_hours(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """تحديد ساعات الهدوء"""
    # الحصول على الإعداد الحالي
    current_setting = db.execute_query("SELECT value FROM settings WHERE key = 'quiet_hours'")
    current = current_setting[0][0] if current_setting else "24h"
    
    keyboard = [
        [InlineKeyboardButton(f"{'✅' if current == '8_18' else '🔕'} 08:00 - 18:00", callback_data="quiet_8_18")],
        [InlineKeyboardButton(f"{'✅' if current == '22_6' else '🔕'} 22:00 - 06:00", callback_data="quiet_22_6")],
        [InlineKeyboardButton(f"{'✅' if current == '12_14' else '🔕'} 12:00 - 14:00", callback_data="quiet_12_14")],
        [InlineKeyboardButton(f"{'✅' if current == '20_22' else '🔕'} 20:00 - 22:00", callback_data="quiet_20_22")],
        [InlineKeyboardButton(f"{'✅' if current == '24h' else '🔊'} 24 ساعة مع صوت", callback_data="quiet_24h")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🔕 ساعات الهدوء\n\nاختر الفترة التي تريد فيها إشعارات صامتة:\n(خارج هذه الفترات ستصل الإشعارات بصوت)",
        reply_markup=reply_markup
    )
    return QUIET_HOURS

async def handle_quiet_hours_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """معالجة اختيار ساعات الهدوء"""
    query = update.callback_query
    await query.answer()
    
    quiet_period = query.data.replace("quiet_", "")
    
    # حفظ في قاعدة البيانات
    db.execute_query(
        "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
        ("quiet_hours", quiet_period)
    )
    
    if quiet_period == "24h":
        message = "🔊 تم تعيين الإشعارات بصوت لمدة 24 ساعة"
    else:
        start_hour, end_hour = quiet_period.split("_")
        message = f"🔕 تم تعيين ساعات الهدوء: `{start_hour}:00 - {end_hour}:00`"
    
    await query.edit_message_text(message, parse_mode='Markdown')
    
    # إعادة تفعيل كيبورد الأدمن بعد فترة قصيرة
    import asyncio
    await asyncio.sleep(1)
    await restore_admin_keyboard(context, update.effective_chat.id)
    
    return ConversationHandler.END

async def admin_logout_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """طلب تأكيد تسجيل خروج الأدمن"""
    keyboard = [
        [InlineKeyboardButton("✅ نعم، تسجيل الخروج", callback_data="confirm_logout")],
        [InlineKeyboardButton("🔙 رجوع", callback_data="cancel_logout")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🚪 **تأكيد تسجيل الخروج**\n\nهل أنت متأكد من رغبتك في تسجيل الخروج من لوحة الأدمن؟",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def handle_logout_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالجة تأكيد تسجيل الخروج"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "confirm_logout":
        # تسجيل الخروج وتنظيف جميع البيانات الخاصة بالأدمن
        global ACTIVE_ADMINS
        user_id = update.effective_user.id
        
        # إزالة الآدمن من قائمة النشطين
        if user_id in ACTIVE_ADMINS:
            ACTIVE_ADMINS.remove(user_id)
        
        context.user_data['is_admin'] = False
        context.user_data.pop('is_admin', None)
        
        # تنظيف أي بيانات أخرى خاصة بالأدمن
        admin_keys = [k for k in context.user_data.keys() if k.startswith('admin_')]
        for key in admin_keys:
            context.user_data.pop(key, None)
        
        # تنظيف أي طلب قيد المعالجة
        context.user_data.pop('processing_order_id', None)
        context.user_data.pop('admin_processing_active', None)
        
        # إنشاء كيبورد المستخدم العادي
        user_id = update.effective_user.id
        language = get_user_language(user_id)
        
        reply_markup = create_main_user_keyboard(language)
        
        await query.edit_message_text(
            "✅ **تم تسجيل الخروج بنجاح**\n\n👋 مرحباً بعودتك كمستخدم عادي\nيمكنك الآن استخدام جميع خدمات البوت",
            parse_mode='Markdown'
        )
        
        await context.bot.send_message(
            update.effective_chat.id,
            "🎯 القائمة الرئيسية\nاختر الخدمة المطلوبة:",
            reply_markup=reply_markup
        )
        
    elif query.data == "cancel_logout":
        await query.edit_message_text(
            "❌ **تم إلغاء تسجيل الخروج**\n\n🔧 لا تزال في لوحة الأدمن\nيمكنك المتابعة في استخدام أدوات الإدارة",
            parse_mode='Markdown'
        )
        
        # إعادة تفعيل كيبورد الأدمن الرئيسي
        await restore_admin_keyboard(context, update.effective_chat.id)

async def handle_back_to_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """العودة للقائمة الرئيسية للأدمن من الأزرار inline"""
    query = update.callback_query
    await query.answer()
    
    # التأكد من أن المستخدم أدمن
    if not context.user_data.get('is_admin', False):
        await query.edit_message_text("❌ هذه الخدمة مخصصة للأدمن فقط!")
        return
    
    await query.edit_message_text("🔧 **تم العودة للقائمة الرئيسية**")
    await restore_admin_keyboard(context, update.effective_chat.id, "🔧 لوحة الأدمن الرئيسية\nاختر الخدمة المطلوبة:")



async def admin_order_inquiry(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """الاستعلام عن طلب"""
    keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data="cancel_order_inquiry")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "🔍 الاستعلام عن طلب\n\nيرجى إرسال معرف الطلب (`16` خانة):",
        parse_mode='Markdown',
        reply_markup=reply_markup
    )
    return ADMIN_ORDER_INQUIRY

async def handle_order_inquiry(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """معالجة الاستعلام عن طلب"""
    order_id = update.message.text.strip()
    

    
    # التحقق من صحة معرف الطلب
    if len(order_id) != 16:
        keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data="cancel_order_inquiry")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "❌ معرف الطلب يجب أن يكون `16` خانة\n\nيرجى إعادة إدخال معرف الطلب:", 
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
        return ADMIN_ORDER_INQUIRY
    
    # البحث عن الطلب
    query = """
        SELECT o.*, u.first_name, u.last_name, u.username 
        FROM orders o 
        JOIN users u ON o.user_id = u.user_id 
        WHERE o.id = ?
    """
    result = db.execute_query(query, (order_id,))
    
    if not result:
        # إعادة تفعيل كيبورد الأدمن
        await update.message.reply_text(f"❌ لم يتم العثور على طلب بالمعرف: {order_id}")
        await restore_admin_keyboard(context, update.effective_chat.id, "🔧 لوحة الأدمن جاهزة")
        return ConversationHandler.END
    
    order = result[0]
    status = order[9]  # حالة الطلب (العمود العاشر: 0-indexed)
    
    # إنشاء رسالة تفاصيل الطلب
    user_name = f"{order[14]} {order[15] or ''}".strip()
    username = order[16] or 'غير محدد'
    
    # تحديد طريقة الدفع
    payment_methods_ar = {
        'shamcash': 'شام كاش',
        'syriatel': 'سيرياتيل كاش',
        'coinex': 'Coinex',
        'binance': 'Binance',
        'payeer': 'Payeer'
    }
    payment_method_ar = payment_methods_ar.get(order[5], order[5])
    
    # تحديد حالة الطلب
    status_text = {
        'pending': '⏳ معلق',
        'completed': '✅ مكتمل',
        'failed': '❌ فاشل'
    }.get(status, status)
    
    order_details = f"""📋 تفاصيل الطلب: `{order_id}`

👤 المستخدم:
📝 الاسم: {user_name}
📱 اسم المستخدم: @{username}
🆔 معرف المستخدم: `{order[1]}`

━━━━━━━━━━━━━━━
📦 تفاصيل الطلب:
📊 الكمية: {order[8]}
🔧 نوع البروكسي: {get_detailed_proxy_type(order[2], order[14] if len(order) > 14 else '')}
🌍 الدولة: {order[3]}
🏠 الولاية: {order[4]}

━━━━━━━━━━━━━━━
💳 تفاصيل الدفع:
💰 طريقة الدفع: {payment_method_ar}
💵 قيمة الطلب: `{order[6]}$`
📄 إثبات الدفع: {"✅ مرفق" if order[7] else "❌ غير مرفق"}

━━━━━━━━━━━━━━━
📊 الحالة: {status_text}
📅 تاريخ الطلب: {order[10]}"""

    if status == 'completed' and order[11]:  # processed_at
        order_details += f"\n⏰ تاريخ المعالجة: {order[11]}"
    
    await update.message.reply_text(order_details, parse_mode='Markdown', reply_markup=ReplyKeyboardRemove())
    
    if status == 'pending':
        # إعادة إرسال الطلب مع إثبات الدفع
        await resend_order_notification(update, context, order)
        await update.message.reply_text("✅ تم إعادة إرسال الطلب للأدمن مع زر المعالجة")
    
    # تنظيف البيانات المؤقتة مع الحفاظ على حالة الأدمن
    clean_user_data_preserve_admin(context)
    await restore_admin_keyboard(context, update.effective_chat.id, "✅ تم الانتهاء من الاستعلام")
    
    return ConversationHandler.END

async def resend_order_notification(update: Update, context: ContextTypes.DEFAULT_TYPE, order: tuple) -> None:
    """إعادة إرسال إشعار الطلب"""
    order_id = order[0]
    
    # تحديد طريقة الدفع باللغة العربية
    payment_methods_ar = {
        'shamcash': 'شام كاش',
        'syriatel': 'سيرياتيل كاش',
        'coinex': 'Coinex',
        'binance': 'Binance',
        'payeer': 'Payeer'
    }
    
    payment_method_ar = payment_methods_ar.get(order[5], order[5])
    
    message = f"""🔔 طلب معاد إرساله

👤 الاسم: `{order[15]} {order[16] or ''}`
📱 اسم المستخدم: @{order[17] or 'غير محدد'}
🆔 معرف المستخدم: `{order[1]}`

━━━━━━━━━━━━━━━
📦 تفاصيل الطلب:
📊 الكمية: {order[8]}
🔧 نوع البروكسي: {get_detailed_proxy_type(order[2], order[14] if len(order) > 14 else '')}
🌍 الدولة: {order[3]}
🏠 الولاية: {order[4]}

━━━━━━━━━━━━━━━
💳 تفاصيل الدفع:
💰 طريقة الدفع: {payment_method_ar}
📄 إثبات الدفع: {"✅ مرفق" if order[7] else "❌ غير مرفق"}

━━━━━━━━━━━━━━━
🔗 معرف الطلب: `{order_id}`
📅 تاريخ الطلب: {order[9]}
📊 الحالة: ⏳ معلق"""

    keyboard = [[InlineKeyboardButton("🔧 معالجة الطلب", callback_data=f"process_{order_id}")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    main_msg = await update.message.reply_text(message, reply_markup=reply_markup, parse_mode='Markdown')
    
    # إرسال إثبات الدفع كرد على رسالة الطلب
    if order[7]:  # payment_proof
        if order[7].startswith("photo:"):
            file_id = order[7].replace("photo:", "")
            await context.bot.send_photo(
                update.effective_chat.id,
                photo=file_id,
                caption=f"📸 إثبات دفع للطلب بمعرف: `{order_id}`",
                parse_mode='Markdown',
                reply_to_message_id=main_msg.message_id
            )
        elif order[7].startswith("text:"):
            text_proof = order[7].replace("text:", "")
            await context.bot.send_message(
                update.effective_chat.id,
                f"📝 إثبات دفع للطلب بمعرف: `{order_id}`\n\nالنص:\n{text_proof}",
                parse_mode='Markdown',
                reply_to_message_id=main_msg.message_id
            )

async def set_static_prices(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """تحديد أسعار الستاتيك"""
    # الحصول على الأسعار الحالية
    static_prices = get_static_prices()
    
    # إنشاء الأزرار مع الأسعار الحالية
    keyboard = [
        [InlineKeyboardButton(f"ISP ({static_prices.get('ISP', '3')}$)", callback_data="set_price_isp")],
        [InlineKeyboardButton(f"ريزيدنتال Crocker ({static_prices.get('Res_1', '4')}$)", callback_data="set_price_verizon")],
        [InlineKeyboardButton(f"ريزيدنتال ({static_prices.get('Res_2', '6')}$)", callback_data="set_price_residential_2")],
        [InlineKeyboardButton(f"Datacenter ({static_prices.get('Datacenter', '12')}$)", callback_data="set_price_datacenter")],
        [InlineKeyboardButton(f"Daily ({static_prices.get('Daily', '0')}$)", callback_data="set_price_daily")],
        [InlineKeyboardButton(f"Weekly ({static_prices.get('Weekly', '0')}$)", callback_data="set_price_weekly")],
        [InlineKeyboardButton("🔙 رجوع", callback_data="cancel_static_prices")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "💰 تعديل أسعار البروكسي الستاتيك\n\nاختر النوع المطلوب تعديل سعره:",
        reply_markup=reply_markup
    )
    return SET_PRICE_STATIC

# معالجات الأزرار الجديدة
async def handle_set_price_isp(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """معالجة تعديل سعر ISP AT&T"""
    query = update.callback_query
    await query.answer()
    
    keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data="cancel_static_prices")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        "💰 تعديل سعر ISP AT&T\n\nأرسل السعر الجديد (أرقام فقط، الفواصل العشرية مسموحة):",
        reply_markup=reply_markup
    )
    context.user_data['setting_price_type'] = 'ISP'
    return SET_PRICE_ISP_ATT

async def handle_set_price_verizon(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """معالجة تعديل سعر Residential Crocker"""
    query = update.callback_query
    await query.answer()
    
    keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data="cancel_static_prices")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        "💰 تعديل سعر Residential Crocker\n\nأرسل السعر الجديد (أرقام فقط، الفواصل العشرية مسموحة):",
        reply_markup=reply_markup
    )
    context.user_data['setting_price_type'] = 'Res_1'
    return SET_PRICE_VERIZON

async def handle_set_price_residential_2(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """معالجة تعديل سعر Residential_2"""
    query = update.callback_query
    await query.answer()
    
    keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data="cancel_static_prices")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        "💰 تعديل سعر Residential_2\n\nأرسل السعر الجديد (أرقام فقط، الفواصل العشرية مسموحة):",
        reply_markup=reply_markup
    )
    context.user_data['setting_price_type'] = 'Res_2'
    return SET_PRICE_RESIDENTIAL_2

async def handle_set_price_daily(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """معالجة تعديل سعر Daily"""
    query = update.callback_query
    await query.answer()
    
    keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data="cancel_static_prices")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        "💰 تعديل سعر Daily\n\nأرسل السعر الجديد (أرقام فقط، الفواصل العشرية مسموحة):",
        reply_markup=reply_markup
    )
    context.user_data['setting_price_type'] = 'Daily'
    return SET_PRICE_DAILY

async def handle_set_price_weekly(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """معالجة تعديل سعر Weekly"""
    query = update.callback_query
    await query.answer()
    
    keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data="cancel_static_prices")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        "💰 تعديل سعر Weekly\n\nأرسل السعر الجديد (أرقام فقط، الفواصل العشرية مسموحة):",
        reply_markup=reply_markup
    )
    context.user_data['setting_price_type'] = 'Weekly'
    return SET_PRICE_WEEKLY

async def handle_set_price_datacenter(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """معالجة تعديل سعر Datacenter"""
    query = update.callback_query
    await query.answer()
    
    keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data="cancel_static_prices")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        "💰 تعديل سعر Datacenter\n\nأرسل السعر الجديد (أرقام فقط، الفواصل العشرية مسموحة):",
        reply_markup=reply_markup
    )
    context.user_data['setting_price_type'] = 'Datacenter'
    return SET_PRICE_WEEKLY

async def handle_individual_static_price_update(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """معالجة تحديث سعر نوع واحد من البروكسي الستاتيك"""
    price_text = update.message.text.strip()
    price_type = context.user_data.get('setting_price_type')
    
    # التحقق من صحة السعر
    try:
        price = float(price_text)
        if price < 0:
            raise ValueError("السعر لا يمكن أن يكون سالبا")
    except ValueError:
        keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data="cancel_static_prices")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            f"❌ يرجى إدخال رقم صحيح فقط (مثال: 5.0)\n\nيرجى إعادة إدخال السعر:",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
        return context.user_data.get('current_state', SET_PRICE_STATIC)
    
    # الحصول على الأسعار الحالية
    current_static_prices = get_static_prices()
    
    # تحديث السعر المحدد
    current_static_prices[price_type] = price_text
    
    # حفظ الأسعار الجديدة في قاعدة البيانات
    prices_string = ','.join([f"{k}:{v}" for k, v in current_static_prices.items()])
    db.execute_query(
        "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
        ("static_prices", prices_string)
    )
    
    # إذا تم تحديث سعر Crocker (Res_1)، حدّث أيضاً verizon_price لأنهما نفس السعر
    if price_type == 'Res_1':
        db.execute_query(
            "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
            ("verizon_price", price_text)
        )
    
    # تحديث رسائل الحزم
    update_static_messages(current_static_prices)
    
    # رسالة نجاح
    type_names = {
        'ISP': 'ISP AT&T',
        'Res_1': 'Residential Crocker', 
        'Res_2': 'Residential_2',
        'Daily': 'Daily',
        'Weekly': 'Weekly'
    }
    
    type_name = type_names.get(price_type, price_type)
    
    await update.message.reply_text(
        f"✅ تم تحديث سعر {type_name} بنجاح!\n\n💰 السعر الجديد: `{price_text}$`\n\n📊 الأسعار الجديدة سارية المفعول فوراً\n\n📢 سيتم إشعار جميع المستخدمين بالأسعار الجديدة...",
        parse_mode='Markdown'
    )
    
    # إشعار جميع المستخدمين بالأسعار الجديدة
    await broadcast_price_update(context, "static_individual", {price_type: price_text, 'type_name': type_name})
    
    # تنظيف البيانات المؤقتة مع الحفاظ على حالة الأدمن
    clean_user_data_preserve_admin(context)
    
    # إعادة تفعيل كيبورد الأدمن الرئيسي
    await restore_admin_keyboard(context, update.effective_chat.id)
    
    return ConversationHandler.END

async def set_res1_prices(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """تحديد أسعار Res1 (ريزيدنتال Crocker)"""
    keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data="cancel_residential_prices")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "💰 تعديل أسعار Res1\n\nيرجى إرسال السعر الجديد (رقم فقط) مثل: `4`",
        parse_mode='Markdown',
        reply_markup=reply_markup
    )
    context.user_data['setting_price_type'] = 'verizon'
    return SET_PRICE_RESIDENTIAL

async def set_res2_prices(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """تحديد أسعار Res2 (ريزيدنتال 6$)"""
    keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data="cancel_residential_prices")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "💰 تعديل أسعار Res2\n\nيرجى إرسال السعر الجديد (رقم فقط) مثل: `6`",
        parse_mode='Markdown',
        reply_markup=reply_markup
    )
    context.user_data['setting_price_type'] = 'att'
    return SET_PRICE_RESIDENTIAL

async def set_daily_prices(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """تحديد أسعار Daily"""
    keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data="cancel_residential_prices")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "💰 تعديل أسعار Daily\n\nيرجى إرسال السعر الجديد (رقم فقط) مثل: `1`",
        parse_mode='Markdown',
        reply_markup=reply_markup
    )
    context.user_data['setting_price_type'] = 'daily'
    return SET_PRICE_RESIDENTIAL

async def set_weekly_prices(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """تحديد أسعار Weekly"""
    keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data="cancel_residential_prices")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "💰 تعديل أسعار Weekly\n\nيرجى إرسال السعر الجديد (رقم فقط) مثل: `5`",
        parse_mode='Markdown',
        reply_markup=reply_markup
    )
    context.user_data['setting_price_type'] = 'weekly'
    return SET_PRICE_RESIDENTIAL

async def set_isp_prices(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """تحديد أسعار ISP"""
    keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data="cancel_isp_prices")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "💰 تعديل أسعار ISP\n\nيرجى إرسال السعر الجديد مثل: `3`",
        parse_mode='Markdown',
        reply_markup=reply_markup
    )
    context.user_data['setting_price_type'] = 'isp'
    return SET_PRICE_ISP

async def set_datacenter_prices(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """تحديد أسعار داتا سينتر"""
    keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data="cancel_datacenter_prices")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "💰 تعديل أسعار داتا سينتر\n\nيرجى إرسال السعر الجديد مثل: `12`",
        parse_mode='Markdown',
        reply_markup=reply_markup
    )
    context.user_data['setting_price_type'] = 'datacenter'
    return SET_PRICE_ISP

async def set_socks_prices(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """قائمة تحديد أسعار السوكس - Inline Keyboard"""
    keyboard = [
        [InlineKeyboardButton("💰 تحديد سعر الواحد 💲", callback_data="set_socks_single")],
        [InlineKeyboardButton("💰 تحديد سعر ال2 💲", callback_data="set_socks_double")],
        [InlineKeyboardButton("💰 تحديد سعر باكج 5 📦", callback_data="set_socks_package5")],
        [InlineKeyboardButton("💰 تحديد سعر باكج 10 📦", callback_data="set_socks_package10")],
        [InlineKeyboardButton("🔙 رجوع", callback_data="back_to_prices_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # التأكد من وجود message أو callback_query
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(
            "💰 إدارة أسعار بروكسي السوكس\nاختر النوع المطلوب تعديل سعره:",
            reply_markup=reply_markup
        )
    else:
        await update.message.reply_text(
            "💰 إدارة أسعار بروكسي السوكس\nاختر النوع المطلوب تعديل سعره:",
            reply_markup=reply_markup
        )
    
    # تحديد حالة لمعالجة زر الرجوع
    context.user_data['last_admin_action'] = 'socks_price_menu'
    
    return SET_PRICE_SOCKS

async def set_socks_single_price(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """تحديد سعر البروكسي الواحد"""
    keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data="cancel_socks_prices")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # إصلاح مشكلة NoneType
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(
            "💰 تعديل سعر البروكسي الواحد\n\nيرجى إرسال السعر الجديد (مثال: `0.5`):",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    else:
        await update.message.reply_text(
            "💰 تعديل سعر البروكسي الواحد\n\nيرجى إرسال السعر الجديد (مثال: `0.5`):",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    context.user_data['socks_price_type'] = 'single'
    return SET_PRICE_SOCKS

async def set_socks_double_price(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """تحديد سعر البروكسي ال2"""
    keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data="cancel_socks_prices")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # إصلاح مشكلة NoneType
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(
            "💰 تعديل سعر البروكسي ال2\n\nيرجى إرسال السعر الجديد (مثال: `0.9`):",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    else:
        await update.message.reply_text(
            "💰 تعديل سعر البروكسي ال2\n\nيرجى إرسال السعر الجديد (مثال: `0.9`):",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    context.user_data['socks_price_type'] = 'double'
    return SET_PRICE_SOCKS

async def set_socks_package5_price(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """تحديد سعر باكج 5 بروكسي"""
    keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data="cancel_socks_prices")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # إصلاح مشكلة NoneType
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(
            "💰 تعديل سعر باكج 5 بروكسي\n\nيرجى إرسال السعر الجديد (مثال: `2.0`):",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    else:
        await update.message.reply_text(
            "💰 تعديل سعر باكج 5 بروكسي\n\nيرجى إرسال السعر الجديد (مثال: `2.0`):",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    context.user_data['socks_price_type'] = 'package5'
    return SET_PRICE_SOCKS

async def set_socks_package10_price(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """تحديد سعر باكج 10 بروكسي"""
    keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data="cancel_socks_prices")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # إصلاح مشكلة NoneType
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(
            "💰 تعديل سعر باكج 10 بروكسي\n\nيرجى إرسال السعر الجديد (مثال: `3.5`):",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    else:
        await update.message.reply_text(
            "💰 تعديل سعر باكج 10 بروكسي\n\nيرجى إرسال السعر الجديد (مثال: `3.5`):",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    context.user_data['socks_price_type'] = 'package10'
    return SET_PRICE_SOCKS

async def handle_static_price_update(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """معالجة تحديث أسعار الستاتيك"""
    prices_text = update.message.text
    

    
    def validate_price(price_str):
        """التحقق من صحة السعر (يجب أن يكون رقم صحيح أو عشري)"""
        try:
            price = float(price_str.strip())
            return price >= 0
        except ValueError:
            return False
    
    # التحقق من صحة المدخلات قبل المعالجة
    # دعم السطور المتعددة والفاصلة
    if "\n" in prices_text or "," in prices_text:
        # أسعار متعددة مثل: Res_1:4\nRes_2:6\nISP:3 أو Res_1:4,Res_2:6,ISP:3
        if "\n" in prices_text:
            price_parts = prices_text.strip().split("\n")
        else:
            price_parts = prices_text.split(",")
        for part in price_parts:
            if ":" in part:
                key, value = part.split(":", 1)
                if not validate_price(value):
                    keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data="cancel_static_prices")]]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    await update.message.reply_text(
                        f"❌ يرجى إدخال رقم صحيح فقط (مثال: 5.0)\n\nيرجى إعادة إدخال الأسعار:",
                        parse_mode='Markdown',
                        reply_markup=reply_markup
                    )
                    return SET_PRICE_STATIC
            else:
                keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data="cancel_static_prices")]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await update.message.reply_text(
                    "❌ تنسيق غير صحيح!\n\n✅ للأسعار المتعددة استخدم:\n`Res_1:4`\n`Res_2:6`\n`ISP:3`\n\nأو في سطر واحد: `Res_1:4,Res_2:6,ISP:3`\n\nيرجى إعادة إدخال الأسعار:",
                    parse_mode='Markdown',
                    reply_markup=reply_markup
                )
                return SET_PRICE_STATIC
    else:
        # سعر واحد لجميع الأنواع
        if not validate_price(prices_text):
            keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data="cancel_static_prices")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(
                f"❌ يرجى إدخال رقم صحيح فقط (مثال: 5.0)\n\nيرجى إعادة إدخال السعر:",
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
            return SET_PRICE_STATIC

    try:
        # تحليل الأسعار الجديدة
        if "\n" in prices_text or "," in prices_text:
            # أسعار متعددة مثل: Res_1:4\nRes_2:6\nISP:3
            if "\n" in prices_text:
                price_parts = prices_text.strip().split("\n")
            else:
                price_parts = prices_text.split(",")
            static_prices = {}
            for part in price_parts:
                if ":" in part:
                    key, value = part.split(":", 1)
                    static_prices[key.strip()] = value.strip()
        else:
            # سعر واحد لجميع الأنواع
            static_prices = {
                "Res_1": prices_text.strip(),
                "Res_2": prices_text.strip(),
                "ISP": prices_text.strip(),
                "Daily": prices_text.strip(),
                "Weekly": prices_text.strip()
            }
        
        # تحديث رسائل الحزم باستخدام الدالة المساعدة
        update_static_messages(static_prices)
        
        # حفظ الأسعار في قاعدة البيانات
        db.execute_query(
            "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
            ("static_prices", prices_text)
        )
        
        await update.message.reply_text(f"✅ تم تحديث أسعار البروكسي الستاتيك بنجاح!\n💰 الأسعار الجديدة: {prices_text}\n\n📢 سيتم إشعار جميع المستخدمين بالأسعار الجديدة...")
        
        # إشعار جميع المستخدمين بالأسعار الجديدة
        await broadcast_price_update(context, "static", static_prices)
        
        # إعادة تفعيل كيبورد الأدمن الرئيسي
        await restore_admin_keyboard(context, update.effective_chat.id)
        
    except Exception as e:
        await update.message.reply_text(f"❌ خطأ في تحديث الأسعار: {str(e)}")
        
        # إعادة تفعيل كيبورد الأدمن الرئيسي حتى في حالة الخطأ
        await restore_admin_keyboard(context, update.effective_chat.id)
    
    return ConversationHandler.END



async def handle_socks_price_update(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """معالجة تحديث أسعار السوكس الفردية"""
    price_text = update.message.text
    price_type = context.user_data.get('socks_price_type', 'single')
    
    def validate_price(price_str):
        """التحقق من صحة السعر (يجب أن يكون رقم صحيح أو عشري)"""
        try:
            price = float(price_str.strip())
            return price >= 0
        except ValueError:
            return False
    
    # التحقق من صحة السعر المدخل
    if not validate_price(price_text):
        keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data="cancel_socks_prices")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            f"❌ يرجى إدخال رقم صحيح فقط (مثال: 2.0)\n\nيرجى إعادة إدخال السعر:",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
        return SET_PRICE_SOCKS

    try:
        # تحديد مفتاح السعر بناءً على النوع المحدد
        price_key_mapping = {
            'single': 'single_proxy',
            'double': 'double_proxy', 
            'package5': '5proxy',
            'package10': '10proxy'
        }
        
        price_key = price_key_mapping.get(price_type, 'single_proxy')
        
        # قراءة الأسعار الحالية من قاعدة البيانات
        current_prices_result = db.execute_query("SELECT value FROM settings WHERE key = 'socks_prices'")
        if current_prices_result:
            current_prices_text = current_prices_result[0][0]
            # تحليل الأسعار الحالية
            if "," in current_prices_text:
                current_prices = {}
                for part in current_prices_text.split(","):
                    if ":" in part:
                        key, value = part.split(":", 1)
                        current_prices[key.strip()] = value.strip()
            else:
                # إذا كان سعر واحد فقط، نضعه كأساس
                current_prices = {
                    'single_proxy': current_prices_text.strip(),
                    'double_proxy': str(float(current_prices_text.strip()) * 1.8),
                    '5proxy': current_prices_text.strip(),
                    '10proxy': '0.7'
                }
        else:
            # أسعار افتراضية إذا لم توجد أسعار مخزنة
            current_prices = {
                'single_proxy': '0.15',
                'double_proxy': '0.25',
                '5proxy': '0.4',
                '10proxy': '0.7'
            }
        
        # تحديث السعر المحدد
        current_prices[price_key] = price_text.strip()
        
        # تحويل الأسعار إلى نص مُنسق
        prices_text = ",".join([f"{key}:{value}" for key, value in current_prices.items()])
        
        # تحديث رسائل الحزم باستخدام الدالة المساعدة
        update_socks_messages(current_prices)
        
        # حفظ الأسعار في قاعدة البيانات
        db.execute_query(
            "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
            ("socks_prices", prices_text)
        )
        
        # رسالة تأكيد حسب نوع السعر
        price_names = {
            'single': 'البروكسي الواحد',
            'double': 'البروكسي ال2',
            'package5': 'باكج 5 بروكسي',
            'package10': 'باكج 10 بروكسي'
        }
        
        price_name = price_names.get(price_type, 'البروكسي')
        await update.message.reply_text(f"✅ تم تحديث سعر {price_name} بنجاح!\n💰 السعر الجديد: ${price_text}\n\n📢 سيتم إشعار جميع المستخدمين بالسعر الجديد...")
        
        # إشعار جميع المستخدمين بالسعر الجديد
        await broadcast_price_update(context, "socks_individual", {price_key: price_text, 'type_name': price_name})
        
        # تنظيف البيانات المؤقتة
        context.user_data.pop('socks_price_type', None)
        
        # إعادة تفعيل كيبورد الأدمن الرئيسي
        await restore_admin_keyboard(context, update.effective_chat.id)
        
    except Exception as e:
        await update.message.reply_text(f"❌ خطأ في تحديث الأسعار: {str(e)}")
        
        # إعادة تفعيل كيبورد الأدمن الرئيسي حتى في حالة الخطأ
        await restore_admin_keyboard(context, update.effective_chat.id)
    
    return ConversationHandler.END

async def reset_user_balance(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """تصفير رصيد مستخدم"""
    context.user_data['lookup_action'] = 'reset_balance'
    keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data="cancel_balance_reset")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "🗑️ تصفير رصيد مستخدم\n\nيرجى إرسال معرف المستخدم أو @username:",
        reply_markup=reply_markup
    )
    return USER_LOOKUP

async def handle_balance_reset(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """معالجة تصفير الرصيد"""
    search_term = update.message.text
    
    # البحث عن المستخدم
    if search_term.startswith('@'):
        username = search_term[1:]
        query = "SELECT * FROM users WHERE username = ?"
        user_result = db.execute_query(query, (username,))
    else:
        try:
            user_id = int(search_term)
            query = "SELECT * FROM users WHERE user_id = ?"
            user_result = db.execute_query(query, (user_id,))
        except ValueError:
            # إعادة تفعيل كيبورد الأدمن
            await update.message.reply_text("❌ معرف المستخدم غير صحيح!")
            await restore_admin_keyboard(context, update.effective_chat.id, "🔧 لوحة الأدمن جاهزة")
            return ConversationHandler.END
    
    if not user_result:
        # إعادة تفعيل كيبورد الأدمن
        await update.message.reply_text("❌ المستخدم غير موجود!")
        await restore_admin_keyboard(context, update.effective_chat.id, "🔧 لوحة الأدمن جاهزة")
        return ConversationHandler.END
    
    user = user_result[0]
    user_id = user[0]
    old_balance = user[5]
    
    # تصفير الرصيد
    db.execute_query("UPDATE users SET referral_balance = 0 WHERE user_id = ?", (user_id,))
    
    # إعادة تفعيل كيبورد الأدمن
    await update.message.reply_text(
        f"✅ تم تصفير رصيد المستخدم بنجاح!\n\n"
        f"👤 الاسم: {user[2]} {user[3] or ''}\n"
        f"💰 الرصيد السابق: {old_balance:.2f}$\n"
        f"💰 الرصيد الجديد: 0.00$"
    )
    await restore_admin_keyboard(context, update.effective_chat.id, "🔧 لوحة الأدمن جاهزة")
    
    return ConversationHandler.END

async def handle_order_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالجة تذكير الطلبات"""
    user_id = update.effective_user.id
    language = get_user_language(user_id)
    
    # التحقق من آخر استخدام للتذكير
    last_reminder = context.user_data.get('last_reminder', 0)
    current_time = datetime.now().timestamp()
    
    # التحقق من مرور 3 ساعات على آخر استخدام
    if current_time - last_reminder < 10800:  # 3 ساعات
        remaining_time = int((10800 - (current_time - last_reminder)) / 60)
        if language == 'ar':
            await update.message.reply_text(
                f"⏰ يمكنك استخدام التذكير مرة أخرى بعد {remaining_time} دقيقة"
            )
        else:
            await update.message.reply_text(
                f"⏰ You can use the reminder again after {remaining_time} minutes"
            )
        return
    
    # البحث عن الطلبات المعلقة للمستخدم
    pending_orders = db.execute_query(
        "SELECT id, created_at FROM orders WHERE user_id = ? AND status = 'pending'",
        (user_id,)
    )
    
    if not pending_orders:
        if language == 'ar':
            await update.message.reply_text("لا توجد لديك طلبات معلقة حالياً.")
        else:
            await update.message.reply_text("You currently have no pending orders.")
        return
    
    # تحديث وقت آخر استخدام
    context.user_data['last_reminder'] = current_time
    
    # إرسال تذكير للأدمن لكل طلب معلق
    user = db.get_user(user_id)
    
    for order in pending_orders:
        order_id = order[0]
        await send_reminder_to_admin(context, order_id, user)
    
    if language == 'ar':
        await update.message.reply_text(
            f"✅ تم إرسال تذكير للأدمن بخصوص `{len(pending_orders)}` طلب معلق",
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            f"✅ Reminder sent to admin about `{len(pending_orders)}` pending order(s)",
            parse_mode='Markdown'
        )

async def send_reminder_to_admin(context: ContextTypes.DEFAULT_TYPE, order_id: str, user: tuple) -> None:
    """إرسال تذكير للأدمن"""
    message = f"""🔔 تذكير بطلب معلق
    
👤 الاسم: `{user[2]} {user[3] or ''}`
📱 اسم المستخدم: @{user[1] or 'غير محدد'}
🆔 معرف المستخدم: `{user[0]}`

💬 مرحباً، لدي طلب معلق بانتظار المعالجة

🔗 معرف الطلب: `{order_id}`
📅 الوقت: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""

    keyboard = [[InlineKeyboardButton("🔧 معالجة الطلب", callback_data=f"process_{order_id}")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if ADMIN_CHAT_ID:
        try:
            await context.bot.send_message(
                ADMIN_CHAT_ID,
                message,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        except Exception as e:
            print(f"خطأ في إرسال التذكير: {e}")

async def confirm_database_clear(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """تأكيد تفريغ قاعدة البيانات"""
    keyboard = [
        [InlineKeyboardButton("✅ نعم، تفريغ البيانات", callback_data="confirm_clear_db")],
        [InlineKeyboardButton("🔙 رجوع", callback_data="cancel_clear_db")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "⚠️ تحذير!\n\nهل أنت متأكد من تفريغ قاعدة البيانات؟\n\n🗑️ سيتم حذف:\n- جميع الطلبات\n- جميع الإحالات\n- جميع السجلات\n\n✅ سيتم الاحتفاظ ب:\n- بيانات المستخدمين\n- بيانات الأدمن\n- إعدادات النظام",
        reply_markup=reply_markup
    )

async def handle_database_clear(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالجة تفريغ قاعدة البيانات"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "confirm_clear_db":
        try:
            # حذف البيانات مع الاحتفاظ ببيانات المستخدمين والأدمن
            db.execute_query("DELETE FROM orders")
            db.execute_query("DELETE FROM referrals") 
            db.execute_query("DELETE FROM logs")
            
            await query.edit_message_text(
                "✅ تم تفريغ قاعدة البيانات بنجاح!\n\n🗑️ تم حذف:\n- جميع الطلبات\n- جميع الإحالات\n- جميع السجلات\n\n✅ تم الاحتفاظ ببيانات المستخدمين والإعدادات"
            )
            
            # إعادة تفعيل كيبورد الأدمن بعد فترة قصيرة
            import asyncio
            await asyncio.sleep(2)
            await restore_admin_keyboard(context, update.effective_chat.id)
        except Exception as e:
            await query.edit_message_text(f"❌ خطأ في تفريغ قاعدة البيانات: {str(e)}")
    
    elif query.data == "cancel_clear_db":
        await query.edit_message_text("❌ تم إلغاء عملية تفريغ قاعدة البيانات")
        
        # إعادة تفعيل كيبورد الأدمن الرئيسي
        await restore_admin_keyboard(context, update.effective_chat.id)

async def handle_cancel_processing(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """معالجة إلغاء معالجة الطلب مؤقتاً"""
    query = update.callback_query
    await query.answer()
    
    order_id = context.user_data.get('processing_order_id')
    if order_id:
        # الحصول على بيانات المستخدم
        user_query = "SELECT user_id FROM orders WHERE id = ?"
        user_result = db.execute_query(user_query, (order_id,))
        
        if user_result:
            user_id = user_result[0][0]
            user_language = get_user_language(user_id)
            
            # إرسال رسالة للمستخدم
            if user_language == 'ar':
                message = f"⏸️ تم توقيف معالجة طلبك مؤقتاً رقم `{order_id}`\n\nسيتم استئناف المعالجة لاحقاً من قبل الأدمن."
            else:
                message = f"⏸️ Processing of your order `{order_id}` has been temporarily stopped\n\nProcessing will resume later by admin."
            
            await context.bot.send_message(user_id, message, parse_mode='Markdown')
        
        # رسالة للأدمن
        await query.edit_message_text(
            f"⏸️ تم إلغاء معالجة الطلب مؤقتاً\n\n🆔 معرف الطلب: {order_id}\n\n📋 الطلب لا يزال في حالة معلق ويمكن استئناف معالجته لاحقاً",
            parse_mode='Markdown'
        )
        
        # تنظيف البيانات المؤقتة
        # إعادة الطلب إلى حالة pending (لا نجاح ولا فشل)
        db.execute_query(
            "UPDATE orders SET status = 'pending' WHERE id = ?",
            (order_id,)
        )

        # تنظيف حالة انتظار رسالة الأدمن
        context.user_data.pop('waiting_for_admin_message', None)
        
        clean_user_data_preserve_admin(context)
        
        # إعادة تفعيل كيبورد الأدمن الرئيسي
        await restore_admin_keyboard(context, update.effective_chat.id)
        
    else:
        await query.edit_message_text("❌ لم يتم العثور على طلب لإلغاء معالجته")
        
        # إعادة تفعيل كيبورد الأدمن الرئيسي حتى في حالة الخطأ
        await restore_admin_keyboard(context, update.effective_chat.id)
    
    return ConversationHandler.END

async def handle_cancel_direct_processing(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالجة إلغاء المعالجة المباشرة"""
    query = update.callback_query
    await query.answer()
    
    order_id = context.user_data.get('processing_order_id')
    if order_id:
        # الحصول على بيانات المستخدم
        user_query = "SELECT user_id FROM orders WHERE id = ?"
        user_result = db.execute_query(user_query, (order_id,))
        
        if user_result:
            user_id = user_result[0][0]
            user_language = get_user_language(user_id)
            
            # إرسال رسالة للمستخدم
            if user_language == 'ar':
                message = f"⏸️ تم توقيف معالجة طلبك مؤقتاً رقم `{order_id}`\n\nسيتم استئناف المعالجة لاحقاً من قبل الأدمن."
            else:
                message = f"⏸️ Processing of your order `{order_id}` has been temporarily stopped\n\nProcessing will resume later by admin."
            
            await context.bot.send_message(user_id, message, parse_mode='Markdown')
        
        # رسالة للأدمن
        await query.edit_message_text(
            f"⏸️ تم إلغاء معالجة الطلب مؤقتاً\n\n🆔 معرف الطلب: {order_id}\n\n📋 الطلب لا يزال في حالة معلق ويمكن استئناف معالجته لاحقاً",
            parse_mode='Markdown'
        )
        
        # تنظيف البيانات المؤقتة
        # إعادة الطلب إلى حالة pending (لا نجاح ولا فشل)
        db.execute_query(
            "UPDATE orders SET status = 'pending' WHERE id = ?",
            (order_id,)
        )

        # تنظيف حالة انتظار رسالة الأدمن
        context.user_data.pop('waiting_for_direct_admin_message', None)
        context.user_data.pop('direct_processing', None)
        
        clean_user_data_preserve_admin(context)
        
        # إعادة تفعيل كيبورد الأدمن
        await restore_admin_keyboard(context, update.effective_chat.id)
    
    else:
        await query.edit_message_text("❌ لم يتم العثور على طلب لإلغاء معالجته")
        
        # إعادة تفعيل كيبورد الأدمن الرئيسي حتى في حالة الخطأ
        await restore_admin_keyboard(context, update.effective_chat.id)

async def send_proxy_with_custom_message_direct(update: Update, context: ContextTypes.DEFAULT_TYPE, custom_message: str) -> None:
    """إرسال البروكسي مع الرسالة المخصصة للمعالجة المباشرة"""
    order_id = context.user_data['processing_order_id']
    
    # الحصول على معلومات المستخدم والطلب
    user_query = """
        SELECT o.user_id, u.first_name, u.last_name 
        FROM orders o 
        JOIN users u ON o.user_id = u.user_id 
        WHERE o.id = ?
    """
    user_result = db.execute_query(user_query, (order_id,))
    
    if user_result:
        user_id, first_name, last_name = user_result[0]
        user_full_name = f"{first_name} {last_name or ''}".strip()
        
        # الحصول على التاريخ والوقت الحاليين
        from datetime import datetime
        now = datetime.now()
        current_date = now.strftime("%Y-%m-%d")
        current_time = now.strftime("%H:%M:%S")
        
        # الحصول على لغة المستخدم وإنشاء رسالة البروكسي
        user_language = get_user_language(user_id)
        
        if user_language == 'ar':
            proxy_message = f"""✅ تم معالجة طلب {user_full_name}

🔐 تفاصيل البروكسي:
{custom_message}

━━━━━━━━━━━━━━━
🆔 معرف الطلب: {order_id}
📅 التاريخ: {current_date}
🕐 الوقت: {current_time}

━━━━━━━━━━━━━━━
✅ تم إنجاز طلبك بنجاح!"""
        else:
            proxy_message = f"""✅ Order processed for {user_full_name}

🔐 Proxy Details:
{custom_message}

━━━━━━━━━━━━━━━
🆔 Order ID: {order_id}
📅 Date: {current_date}
🕐 Time: {current_time}

━━━━━━━━━━━━━━━
✅ Your order has been completed successfully!"""
        
        # اقتطاع الرصيد من المستخدم عند إرسال البروكسي (هذا هو التوقيت الصحيح)
        order_query = "SELECT user_id, payment_amount, proxy_type FROM orders WHERE id = ?"
        order_result = db.execute_query(order_query, (order_id,))
        
        if order_result:
            order_user_id, payment_amount, proxy_type = order_result[0]
            
            # اقتطاع الرصيد (مع السماح بالرصيد السالب لمنع التحايل)
            try:
                db.deduct_credits(
                    order_user_id, 
                    payment_amount, 
                    'proxy_purchase', 
                    order_id, 
                    f"شراء بروكسي {proxy_type}",
                    allow_negative=True  # السماح بالرصيد السالب
                )
                logger.info(f"تم اقتطاع {payment_amount} نقطة من المستخدم {order_user_id} للطلب {order_id}")
            except Exception as deduct_error:
                logger.error(f"Error deducting points for order {order_id}: {deduct_error}")
        
        # إرسال البروكسي للمستخدم
        await context.bot.send_message(user_id, proxy_message, parse_mode='Markdown')
        
        # تحديث حالة الطلب
        proxy_details = {
            'admin_message': custom_message,
            'processed_date': current_date,
            'processed_time': current_time
        }
        
        # تسجيل الطلب كمكتمل ومعالج فعلياً
        db.execute_query(
            "UPDATE orders SET status = 'completed', processed_at = CURRENT_TIMESTAMP, proxy_details = ?, truly_processed = TRUE WHERE id = ?",
            (json.dumps(proxy_details), order_id)
        )
        
        # التحقق من إضافة رصيد الإحالة لأول عملية شراء
        await check_and_add_referral_bonus(context, user_id, order_id)
        
        # تنظيف البيانات المؤقتة
        context.user_data.pop('waiting_for_direct_admin_message', None)
        context.user_data.pop('direct_processing', None)
        clean_user_data_preserve_admin(context)
        
        # إرسال رسالة تأكيد للأدمن مع خيار العودة للطلبات المعلقة
        keyboard = [
            [InlineKeyboardButton("🔄 معالجة طلب آخر", callback_data="back_to_pending_orders")],
            [InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="admin_main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        success_message = f"""✅ **تم إنجاز الطلب بنجاح!**

🆔 معرف الطلب: {order_id}
👤 المستخدم: {user_full_name}
📅 التاريخ: {current_date} - {current_time}

━━━━━━━━━━━━━━━
✅ تم إرسال البروكسي للمستخدم بنجاح
✅ تم تحديث حالة الطلب إلى مكتمل
✅ تمت معالجة رصيد الإحالة (إن وجد)

🎯 **جاهز لمعالجة المزيد من الطلبات!**

💡 **نصيحة:** يمكنك الآن معالجة عدة طلبات متتالية بسرعة دون قيود!"""

        await update.message.reply_text(
            success_message,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

async def handle_cancel_user_lookup(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """معالجة إلغاء البحث عن مستخدم"""
    query = update.callback_query
    await query.answer()
    
    # تنظيف بيانات المستخدم
    context.user_data.pop('lookup_action', None)
    
    await query.edit_message_text("❌ تم إلغاء البحث عن المستخدم")
    
    # إعادة تفعيل كيبورد الأدمن الرئيسي
    await restore_admin_keyboard(context, update.effective_chat.id)
    
    return ConversationHandler.END

async def handle_cancel_referral_amount(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """معالجة إلغاء تحديد قيمة الإحالة"""
    query = update.callback_query
    await query.answer()
    
    # تنظيف البيانات المؤقتة مع الحفاظ على حالة الأدمن
    clean_user_data_preserve_admin(context)
    
    await query.edit_message_text("❌ تم إلغاء تحديد قيمة الإحالة")
    
    # إعادة تفعيل كيبورد الأدمن الرئيسي
    await restore_admin_keyboard(context, update.effective_chat.id)
    
    return ConversationHandler.END

async def handle_cancel_credit_price(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """معالجة إلغاء تحديد سعر النقطة"""
    query = update.callback_query
    await query.answer()
    
    # تنظيف البيانات المؤقتة مع الحفاظ على حالة الأدمن
    clean_user_data_preserve_admin(context)
    
    await query.edit_message_text("❌ تم إلغاء تحديد سعر النقطة")
    
    # إعادة تفعيل كيبورد الأدمن الرئيسي
    await restore_admin_keyboard(context, update.effective_chat.id)
    
    return ConversationHandler.END

async def handle_cancel_order_inquiry(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """معالجة إلغاء الاستعلام عن طلب"""
    query = update.callback_query
    await query.answer()
    
    # تنظيف البيانات المؤقتة مع الحفاظ على حالة الأدمن
    clean_user_data_preserve_admin(context)
    
    await query.edit_message_text("❌ تم إلغاء الاستعلام عن الطلب")
    
    # إعادة تفعيل كيبورد الأدمن الرئيسي
    await restore_admin_keyboard(context, update.effective_chat.id)
    
    return ConversationHandler.END

async def handle_cancel_static_prices(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """معالجة إلغاء تعديل أسعار الستاتيك"""
    query = update.callback_query
    await query.answer()
    
    # تنظيف البيانات المؤقتة مع الحفاظ على حالة الأدمن
    clean_user_data_preserve_admin(context)
    
    await query.edit_message_text("❌ تم إلغاء تعديل أسعار الستاتيك")
    
    # إعادة تفعيل كيبورد الأدمن الرئيسي
    await restore_admin_keyboard(context, update.effective_chat.id)
    
    return ConversationHandler.END

async def handle_cancel_socks_prices(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """معالجة إلغاء تعديل أسعار السوكس"""
    query = update.callback_query
    await query.answer()
    
    # تنظيف البيانات المؤقتة مع الحفاظ على حالة الأدمن
    clean_user_data_preserve_admin(context)
    
    await query.edit_message_text("❌ تم إلغاء تعديل أسعار السوكس")
    
    # إعادة تفعيل كيبورد الأدمن الرئيسي
    await restore_admin_keyboard(context, update.effective_chat.id)
    
    return ConversationHandler.END

async def handle_cancel_balance_reset(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """معالجة إلغاء تصفير الرصيد"""
    query = update.callback_query
    await query.answer()
    
    # تنظيف البيانات المؤقتة مع الحفاظ على حالة الأدمن
    clean_user_data_preserve_admin(context)
    
    await query.edit_message_text("❌ تم إلغاء تصفير رصيد المستخدم")
    
    # إعادة تفعيل كيبورد الأدمن الرئيسي
    await restore_admin_keyboard(context, update.effective_chat.id)
    
    return ConversationHandler.END

async def handle_cancel_payment_proof(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """معالجة إلغاء إرسال إثبات الدفع"""
    try:
        query = update.callback_query
        await query.answer()
        
        user_id = update.effective_user.id
        language = get_user_language(user_id)
        
        print(f"🚫 المستخدم {user_id} ألغى إرسال إثبات الدفع")
        
        # تسجيل العملية
        try:
            db.log_action(user_id, "payment_proof_cancelled", "User cancelled payment proof submission")
        except:
            pass
        
        # تنظيف البيانات المؤقتة مع الحفاظ على حالة الأدمن (إذا كان أدمن)
        clean_user_data_preserve_admin(context)
        
        if language == 'ar':
            message = "❌ تم إلغاء إرسال إثبات الدفع\n\n🔄 يمكنك البدء من جديد في أي وقت"
        else:
            message = "❌ Payment proof submission cancelled\n\n🔄 You can start again anytime"
        
        await query.edit_message_text(message, parse_mode='Markdown')
        
        # انتظار قليل قبل إعادة التوجيه
        await asyncio.sleep(1)
        
        # للمستخدم العادي - إعادة توجيه للقائمة الرئيسية
        try:
            await start(update, context)
            print(f"✅ تم إعادة توجيه المستخدم {user_id} للقائمة الرئيسية بعد الإلغاء")
        except Exception as e:
            print(f"⚠️ خطأ في إعادة التوجيه للمستخدم {user_id}: {e}")
        
        return ConversationHandler.END
        
    except Exception as e:
        print(f"❌ خطأ في معالجة إلغاء إثبات الدفع للمستخدم {update.effective_user.id}: {e}")
        try:
            # تنظيف البيانات على أي حال مع الحفاظ على حالة الأدمن
            clean_user_data_preserve_admin(context)
            await update.callback_query.answer("❌ تم الإلغاء")
        except:
            pass
        return ConversationHandler.END

async def handle_order_completed_success(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """معالجة إنهاء الطلب بنجاح وإنهاء ConversationHandler"""
    query = update.callback_query
    await query.answer()
    
    order_id = context.user_data.get('processing_order_id')
    if order_id:
        # تنظيف جميع البيانات المؤقتة مع الحفاظ على حالة الأدمن
        clean_user_data_preserve_admin(context)
    
    await query.edit_message_text(
        f"✅ تم إنهاء الطلب بنجاح!\n\n🆔 معرف الطلب: {order_id}\n\n📋 تم نقل الطلب إلى الطلبات المكتملة.\n\n🔄 يمكنك الآن معالجة طلبات أخرى.",
        parse_mode='Markdown'
    )
    
    # إعادة تفعيل كيبورد الأدمن الرئيسي
    await restore_admin_keyboard(context, update.effective_chat.id)
    
    # إنهاء ConversationHandler بشكل صحيح
    return ConversationHandler.END

async def handle_cancel_custom_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """معالجة إلغاء إرسال الرسالة المخصصة"""
    query = update.callback_query
    await query.answer()
    
    # تنظيف البيانات المؤقتة مع الحفاظ على حالة الأدمن
    clean_user_data_preserve_admin(context)
    
    await query.edit_message_text("❌ تم إلغاء إرسال الرسالة المخصصة")
    
    # إعادة تفعيل كيبورد الأدمن الرئيسي
    await restore_admin_keyboard(context, update.effective_chat.id)
    
    return ConversationHandler.END

async def handle_cancel_proxy_setup(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """معالجة إلغاء إعداد البروكسي"""
    query = update.callback_query
    await query.answer()
    
    # تنظيف البيانات المؤقتة مع الحفاظ على حالة الأدمن
    clean_user_data_preserve_admin(context)
    
    await query.edit_message_text("❌ تم إلغاء إعداد البروكسي")
    
    # إعادة تفعيل كيبورد الأدمن الرئيسي
    await restore_admin_keyboard(context, update.effective_chat.id)
    
    return ConversationHandler.END

async def cleanup_incomplete_operations(context: ContextTypes.DEFAULT_TYPE, user_id: int, operation_type: str = "all") -> bool:
    """
    تنظيف العمليات المعلقة وغير المكتملة لمنع توقف الكيبورد أو البوت
    
    Args:
        context: سياق البوت
        user_id: معرف المستخدم
        operation_type: نوع العملية للتنظيف ("all", "admin", "user", "conversation")
    
    Returns:
        bool: True إذا تم التنظيف بنجاح
    """
    try:
        cleaned_operations = []
        
        # تنظيف عمليات الأدمن المعلقة
        if operation_type in ["all", "admin"]:
            admin_keys = [
                'processing_order_id', 'admin_processing_active', 'admin_proxy_type',
                'admin_proxy_address', 'admin_proxy_port', 'admin_proxy_country',
                'admin_proxy_state', 'admin_proxy_username', 'admin_proxy_password',
                'admin_thank_message', 'admin_input_state', 'current_country_code'
            ]
            for key in admin_keys:
                if context.user_data.pop(key, None) is not None:
                    cleaned_operations.append(f"admin_{key}")
        
        # تنظيف عمليات المستخدم المعلقة
        if operation_type in ["all", "user"]:
            user_keys = [
                'proxy_type', 'selected_country', 'selected_country_code',
                'selected_state', 'payment_method', 'current_order_id',
                'waiting_for', 'last_reminder'
            ]
            for key in user_keys:
                if context.user_data.pop(key, None) is not None:
                    cleaned_operations.append(f"user_{key}")
        
        # تنظيف عمليات المحادثة المعلقة
        if operation_type in ["all", "conversation"]:
            conversation_keys = [
                'password_change_step', 'lookup_action', 'popup_text',
                'broadcast_type', 'broadcast_message', 'broadcast_users_input',
                'broadcast_valid_users'
            ]
            for key in conversation_keys:
                if context.user_data.pop(key, None) is not None:
                    cleaned_operations.append(f"conversation_{key}")
        
        # تسجيل العمليات المنظفة في السجل
        if cleaned_operations:
            db.log_action(user_id, "cleanup_incomplete_operations", 
                         f"Cleaned: {', '.join(cleaned_operations)}")
            logger.info(f"Cleaned {len(cleaned_operations)} incomplete operations for user {user_id}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error cleaning incomplete operations for user {user_id}: {e}")
        return False

async def force_reset_user_state(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    إعادة تعيين حالة المستخدم بالكامل في حالة الطوارئ
    يمكن استخدامها عند توقف الكيبورد أو البوت
    """
    user_id = update.effective_user.id
    
    try:
        # تنظيف جميع البيانات المؤقتة
        context.user_data.clear()  # تبسيط التنظيف
        
        # التحقق من نوع المستخدم وإعادة تفعيل الكيبورد المناسب
        is_admin = context.user_data.get('is_admin', False) or user_id in ACTIVE_ADMINS
        
        if is_admin:
            # إعادة تفعيل كيبورد الأدمن
            context.user_data['is_admin'] = True
            await restore_admin_keyboard(context, update.effective_chat.id, 
                                       "🔧 تم إعادة تعيين حالة الأدمن بنجاح")
        else:
            # إعادة تفعيل كيبورد المستخدم العادي
            language = get_user_language(user_id)
            keyboard = [
                [KeyboardButton(MESSAGES[language]['main_menu_buttons'][0])],  # طلب بروكسي ستاتيك
                [KeyboardButton(MESSAGES[language]['main_menu_buttons'][1])],  # طلب بروكسي سوكس
                [KeyboardButton(MESSAGES[language]['main_menu_buttons'][2]), KeyboardButton(MESSAGES[language]['main_menu_buttons'][3])],  # تجربة ستاتيك + الرصيد
                [KeyboardButton(MESSAGES[language]['main_menu_buttons'][5]), KeyboardButton(MESSAGES[language]['main_menu_buttons'][4])],  # الإعدادات + تذكير بطلباتي
                [KeyboardButton(MESSAGES[language]['main_menu_buttons'][6])]  # المزيد من الخدمات
            ]
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            
            await context.bot.send_message(
                update.effective_chat.id,
                "🔄 تم إعادة تعيين حالة البوت بنجاح\n\n" + MESSAGES[language]['welcome'],
                reply_markup=reply_markup
            )
        
        # تسجيل العملية
        db.log_action(user_id, "force_reset_user_state", "Emergency state reset completed")
        logger.info(f"Force reset completed for user {user_id}")
        
    except Exception as e:
        logger.error(f"Error in force reset for user {user_id}: {e}")
        
        # في حالة فشل كل شيء، أرسل رسالة بسيطة
        try:
            await context.bot.send_message(
                update.effective_chat.id,
                "❌ حدث خطأ في إعادة التعيين. يرجى استخدام /start لإعادة تشغيل البوت"
            )
        except:
            pass

async def handle_stuck_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    معالجة المحادثات العالقة التي لا تستجيب
    """
    user_id = update.effective_user.id
    is_admin = context.user_data.get('is_admin', False) or user_id in ACTIVE_ADMINS
    
    try:
        logger.warning(f"Stuck conversation detected for user {user_id}")
        
        # تنظيف العمليات المعلقة مع الحفاظ على حالة الأدمن
        clean_user_data_preserve_admin(context)
        
        # إرسال رسالة توضيحية وإعادة الكيبورد المناسب
        if update.message:
            await update.message.reply_text(
                "🔄 تم اكتشاف محادثة عالقة وتم تنظيفها\n"
                "يمكنك الآن المتابعة بشكل طبيعي",
                reply_markup=ReplyKeyboardRemove()
            )
        elif update.callback_query:
            await update.callback_query.answer("تم إعادة تعيين الحالة")
            await update.callback_query.message.reply_text(
                "🔄 تم اكتشاف محادثة عالقة وتم تنظيفها\n"
                "يمكنك الآن المتابعة بشكل طبيعي"
            )
        
        # إعادة الكيبورد المناسب حسب نوع المستخدم
        if is_admin:
            await restore_admin_keyboard(context, update.effective_chat.id, "🔄 تم إعادة التعيين")
        else:
            await start(update, context)
        
        return ConversationHandler.END
        
    except Exception as e:
        logger.error(f"Error handling stuck conversation for user {user_id}: {e}")
        try:
            clean_user_data_preserve_admin(context)
            if update.message:
                await update.message.reply_text("⚠️ حدث خطأ. يرجى استخدام /start لإعادة التشغيل")
        except:
            pass
        return ConversationHandler.END

async def auto_cleanup_expired_operations(context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    تنظيف تلقائي للعمليات المنتهية الصلاحية (يعمل كل ساعة)
    """
    try:
        # الحصول على جميع المستخدمين النشطين
        active_users = db.execute_query("""
            SELECT DISTINCT user_id 
            FROM logs 
            WHERE timestamp > datetime('now', '-24 hours')
        """)
        
        cleanup_count = 0
        
        for user_tuple in active_users:
            user_id = user_tuple[0]
            
            # تحقق من وجود عمليات معلقة قديمة (أكثر من 30 دقيقة)
            old_operations = db.execute_query("""
                SELECT COUNT(*) FROM logs 
                WHERE user_id = ? 
                AND action LIKE '%_started' 
                AND timestamp < datetime('now', '-30 minutes')
                AND user_id NOT IN (
                    SELECT user_id FROM logs 
                    WHERE action LIKE '%_completed' 
                    AND timestamp > datetime('now', '-30 minutes')
                )
            """, (user_id,))
            
            if old_operations and old_operations[0][0] > 0:
                # تنظيف البيانات المعلقة
                # ملاحظة: هذا يتطلب الوصول لـ user_data الخاص بالمستخدم
                # في التطبيق الحقيقي، يمكن حفظ البيانات في قاعدة البيانات
                cleanup_count += 1
                db.log_action(user_id, "auto_cleanup_expired", "Cleaned expired operations")
        
        if cleanup_count > 0:
            logger.info(f"Auto-cleaned expired operations for {cleanup_count} users")
            
    except Exception as e:
        logger.error(f"Error in auto cleanup: {e}")


async def show_user_statistics(update: Update, context: ContextTypes.DEFAULT_TYPE, offset: int = 0) -> None:
    """عرض إحصائيات المستخدمين مرتبة حسب عدد الإحالات مع دعم التصفح"""
    # الحصول على العدد الإجمالي للمستخدمين
    total_count_query = "SELECT COUNT(*) FROM users"
    total_users = db.execute_query(total_count_query)[0][0]
    
    # حجم الصفحة الواحدة
    page_size = 20
    
    stats_query = """
        SELECT u.first_name, u.last_name, u.username, u.user_id,
               COUNT(r.id) as referral_count, u.referral_balance
        FROM users u
        LEFT JOIN referrals r ON u.user_id = r.referrer_id
        GROUP BY u.user_id
        ORDER BY referral_count DESC
        LIMIT ? OFFSET ?
    """
    
    users_stats = db.execute_query(stats_query, (page_size, offset))
    
    if not users_stats:
        if offset == 0:
            await update.message.reply_text("لا توجد إحصائيات متاحة")
        else:
            await update.message.reply_text("📊 هذا كل شيء!\n\n✅ تم عرض جميع المستخدمين في قاعدة البيانات")
        return
    
    # تحديد رقم الصفحة الحالية
    current_page = (offset // page_size) + 1
    total_pages = (total_users + page_size - 1) // page_size
    
    message = f"📊 إحصائيات المستخدمين (الصفحة {current_page} من {total_pages})\n"
    message += f"👥 المستخدمون {offset + 1} إلى {min(offset + page_size, total_users)} من أصل {total_users}\n\n"
    
    for i, user_stat in enumerate(users_stats, 1):
        global_index = offset + i
        name = f"{user_stat[0]} {user_stat[1] or ''}"
        username = f"@{user_stat[2]}" if user_stat[2] else "بدون معرف"
        referral_count = user_stat[4]
        balance = user_stat[5]
        
        message += f"{global_index}. {name}\n"
        message += f"   👤 {username}\n"
        message += f"   👥 الإحالات: {referral_count}\n"
        message += f"   💰 الرصيد: {balance:.2f}$\n\n"
    
    # إضافة زر "عرض المزيد" إذا كان هناك مستخدمون أكثر
    keyboard = []
    if offset + page_size < total_users:
        keyboard.append([InlineKeyboardButton("📄 عرض المزيد", callback_data=f"show_more_users_{offset + page_size}")])
    
    reply_markup = InlineKeyboardMarkup(keyboard) if keyboard else None
    
    # فحص إذا كانت الرسالة من callback query أو message عادية
    if update.callback_query:
        await update.callback_query.edit_message_text(message, reply_markup=reply_markup)
    else:
        await update.message.reply_text(message, reply_markup=reply_markup)

# وظائف التقسيم والتنقل
def paginate_items(items, page=0, items_per_page=8):
    """تقسيم القوائم لصفحات"""
    start = page * items_per_page
    end = start + items_per_page
    return list(items.items())[start:end], len(items) > end

def create_paginated_keyboard(items, callback_prefix, page=0, items_per_page=8, language='ar'):
    """إنشاء كيبورد مقسم بأزرار التنقل"""
    keyboard = []
    
    # إضافة زر "غير ذلك" في المقدمة مع إيموجي مميز
    other_text = "🔧 غير ذلك" if language == 'ar' else "🔧 Other"
    keyboard.append([InlineKeyboardButton(other_text, callback_data=f"{callback_prefix}other")])
    
    # الحصول على العناصر للصفحة الحالية
    page_items, has_more = paginate_items(items, page, items_per_page)
    
    # إضافة عناصر الصفحة الحالية
    for code, name in page_items:
        keyboard.append([InlineKeyboardButton(name, callback_data=f"{callback_prefix}{code}")])
    
    # إضافة أزرار التنقل
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("◀️ السابق" if language == 'ar' else "◀️ Previous", 
                                               callback_data=f"{callback_prefix}page_{page-1}"))
    if has_more:
        nav_buttons.append(InlineKeyboardButton("التالي ▶️" if language == 'ar' else "Next ▶️", 
                                               callback_data=f"{callback_prefix}page_{page+1}"))
    
    if nav_buttons:
        keyboard.append(nav_buttons)
    
    return InlineKeyboardMarkup(keyboard)

def get_states_for_country(country_code, proxy_type='static', proxy_subtype='residential'):
    """الحصول على قائمة الولايات/المناطق للدولة المحددة حسب نوع البروكسي"""
    
    # للبروكسي الستاتيك
    if proxy_type == 'static':
        if proxy_subtype == 'residential':
            # الستاتيك الريزيدنتال: الولايات المتحدة فقط لها ولايات، باقي البلدان بدون ولايات
            if country_code == 'US':
                return US_STATES_STATIC_RESIDENTIAL
            else:
                return None  # بريطانيا، فرنسا، ألمانيا بدون ولايات
        elif proxy_subtype == 'residential_verizon':
            # الستاتيك Verizon ريزيدنتال: الولايات المتحدة فقط مع ولايات محددة
            if country_code == 'US':
                return US_STATES_STATIC_VERIZON
            else:
                return None
        elif proxy_subtype == 'residential_crocker':
            # الستاتيك Crocker ريزيدنتال: الولايات المتحدة فقط مع ولاية واحدة
            if country_code == 'US':
                return US_STATES_STATIC_CROCKER
            else:
                return None
        elif proxy_subtype == 'isp':
            # الستاتيك ISP: الولايات المتحدة فقط
            if country_code == 'US':
                return US_STATES_STATIC_ISP
            else:
                return None
    
    # للبروكسي السوكس (النظام القديم)
    elif proxy_type == 'socks':
        states_map = {
            'US': US_STATES,
            'UK': UK_STATES,
            'DE': DE_STATES,
            'FR': FR_STATES,
            'CA': CA_STATES,
            'AU': AU_STATES,
            'AT': AT_STATES,
            'IT': IT_STATES,
            'ES': ES_STATES,
            'NL': NL_STATES,
            'BE': BE_STATES,
            'CH': CH_STATES,
            'RU': RU_STATES,
            'JP': JP_STATES,
            'BR': BR_STATES,
            'MX': MX_STATES,
            'IN': IN_STATES
        }
        return states_map.get(country_code, None)
    
    return None

async def show_proxy_preview(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """عرض معاينة البروكسي للأدمن قبل الإرسال"""
    order_id = context.user_data['processing_order_id']
    
    # الحصول على معلومات المستخدم والطلب
    user_query = """
        SELECT o.user_id, u.first_name, u.last_name, u.username
        FROM orders o 
        JOIN users u ON o.user_id = u.user_id 
        WHERE o.id = ?
    """
    user_result = db.execute_query(user_query, (order_id,))
    
    if user_result:
        user_id, first_name, last_name, username = user_result[0]
        user_full_name = f"{first_name} {last_name or ''}".strip()
        
        # الحصول على التاريخ والوقت الحاليين
        from datetime import datetime
        now = datetime.now()
        current_date = now.strftime("%Y-%m-%d")
        current_time = now.strftime("%H:%M:%S")
        
        # إنشاء رسالة المعاينة
        preview_message = f"""📋 مراجعة البروكسي قبل الإرسال

👤 **المستخدم:**
الاسم: {user_full_name}
اسم المستخدم: @{username or 'غير محدد'}
المعرف: `{user_id}`

🔐 **تفاصيل البروكسي:**
العنوان: `{context.user_data['admin_proxy_address']}`
البورت: `{context.user_data['admin_proxy_port']}`
الدولة: {context.user_data.get('admin_proxy_country', 'غير محدد')}
الولاية: {context.user_data.get('admin_proxy_state', 'غير محدد')}
اسم المستخدم: `{context.user_data['admin_proxy_username']}`
كلمة المرور: `{context.user_data['admin_proxy_password']}`

📅 **التاريخ والوقت:**
التاريخ: {current_date}
الوقت: {current_time}

💬 **رسالة الشكر:**
{context.user_data['admin_thank_message']}

━━━━━━━━━━━━━━━
🆔 معرف الطلب: {order_id}

تم إرسال البروكسي للمستخدم تلقائياً."""

        # إرسال البروكسي للمستخدم مباشرة
        await send_proxy_to_user_direct(update, context, context.user_data.get('admin_thank_message', ''))
        
        # زر واحد لإنهاء الطلب
        keyboard = [
            [InlineKeyboardButton("✅ تم إنجاز الطلب بنجاح!", callback_data="order_completed_success")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(preview_message, reply_markup=reply_markup, parse_mode='Markdown')

async def show_broadcast_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """عرض قائمة البث"""
    keyboard = [
        [InlineKeyboardButton("📢 إرسال للجميع", callback_data="broadcast_all")],
        [InlineKeyboardButton("👥 إرسال لمستخدمين مخصصين", callback_data="broadcast_custom")],
        [InlineKeyboardButton("🔙 العودة", callback_data="back_to_admin")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "📢 قائمة البث\n\nاختر نوع الإرسال:",
        reply_markup=reply_markup
    )

async def handle_broadcast_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """معالجة اختيار نوع البث"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "broadcast_all":
        context.user_data['broadcast_type'] = 'all'
        keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data="cancel_broadcast")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "📢 إرسال إعلان للجميع\n\nيرجى كتابة الرسالة التي تريد إرسالها لجميع المستخدمين:",
            reply_markup=reply_markup
        )
        return BROADCAST_MESSAGE
    
    elif query.data == "broadcast_custom":
        context.user_data['broadcast_type'] = 'custom'
        keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data="cancel_broadcast")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "👥 إرسال لمستخدمين مخصصين\n\nيرجى إدخال معرفات المستخدمين أو أسماء المستخدمين:\n\n"
            "الشكل المطلوب:\n"
            "• مستخدم واحد: 123456789 أو @username\n"
            "• عدة مستخدمين: 123456789 - @user1 - 987654321\n\n"
            "⚠️ ملاحظة: استخدم  -  (مسافة قبل وبعد الشرطة) للفصل بين المستخدمين",
            reply_markup=reply_markup
        )
        return BROADCAST_USERS
    
    return ConversationHandler.END

async def handle_broadcast_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """معالجة إدخال رسالة البث (نص أو صورة مع نص)"""
    
    # فحص إذا كانت الرسالة تحتوي على صورة
    if update.message.photo:
        file_id = update.message.photo[-1].file_id
        context.user_data['broadcast_photo'] = file_id
        message_text = update.message.caption or ""
        context.user_data['broadcast_message'] = message_text
    elif update.message.text:
        message_text = update.message.text
        context.user_data['broadcast_message'] = message_text
        context.user_data['broadcast_photo'] = None
    else:
        await update.message.reply_text("❌ يرجى إرسال رسالة نصية أو صورة مع نص!")
        return BROADCAST_MESSAGE
    
    broadcast_type = context.user_data.get('broadcast_type', 'all')
    
    if broadcast_type == 'all':
        # عرض المعاينة للإرسال للجميع
        user_count = db.execute_query("SELECT COUNT(*) FROM users")[0][0]
        
        preview_text = f"""📢 معاينة الإعلان

👥 المستقبلون: جميع المستخدمين ({user_count} مستخدم)

📝 الرسالة:
{message_text}

━━━━━━━━━━━━━━━
هل تريد إرسال هذا الإعلان؟"""

        keyboard = [
            [InlineKeyboardButton("✅ إرسال", callback_data="confirm_broadcast")],
            [InlineKeyboardButton("🔙 رجوع", callback_data="cancel_broadcast")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(preview_text, reply_markup=reply_markup)
        return BROADCAST_CONFIRM

    
    elif broadcast_type == 'custom':
        # للمستخدمين المخصصين - استخدام handle_broadcast_custom_message
        return await handle_broadcast_custom_message(update, context)
    
    return ConversationHandler.END

async def handle_broadcast_users(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """معالجة إدخال المستخدمين المخصصين"""
    users_input = update.message.text
    context.user_data['broadcast_users_input'] = users_input
    
    # تحليل المدخلات
    users_list = [user.strip() for user in users_input.split(' - ')]
    valid_users = []
    invalid_users = []
    
    for user in users_list:
        if user.startswith('@'):
            # البحث باسم المستخدم
            username = user[1:]
            user_result = db.execute_query("SELECT user_id, first_name FROM users WHERE username = ?", (username,))
            if user_result:
                valid_users.append((user_result[0][0], user_result[0][1], user))
            else:
                invalid_users.append(user)
        else:
            try:
                # البحث بالمعرف
                user_id = int(user)
                user_result = db.execute_query("SELECT first_name FROM users WHERE user_id = ?", (user_id,))
                if user_result:
                    valid_users.append((user_id, user_result[0][0], user))
                else:
                    invalid_users.append(user)
            except ValueError:
                invalid_users.append(user)
    
    context.user_data['broadcast_valid_users'] = valid_users
    
    if not valid_users:
        await update.message.reply_text("❌ لم يتم العثور على أي مستخدم صحيح. يرجى المحاولة مرة أخرى.")
        return BROADCAST_USERS
    
    # عرض قائمة المستخدمين الصحيحين والخاطئين
    preview_text = f"👥 **المستخدمون المختارون:**\n\n"
    
    if valid_users:
        preview_text += "✅ **مستخدمون صحيحون:**\n"
        for user_id, name, original in valid_users:
            preview_text += f"• {name} ({original})\n"
    
    if invalid_users:
        preview_text += f"\n❌ **مستخدمون غير موجودون:**\n"
        for user in invalid_users:
            preview_text += f"• {user}\n"
    
    preview_text += f"\nيرجى كتابة الرسالة التي تريد إرسالها لـ {len(valid_users)} مستخدم:"
    
    keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data="cancel_broadcast")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(preview_text, reply_markup=reply_markup, parse_mode='Markdown')
    return BROADCAST_MESSAGE

async def handle_broadcast_custom_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """معالجة رسالة البث للمستخدمين المخصصين"""
    message_text = update.message.text
    context.user_data['broadcast_message'] = message_text
    
    valid_users = context.user_data.get('broadcast_valid_users', [])
    
    # عرض المعاينة النهائية
    preview_text = f"""📢 معاينة الإعلان المخصص

👥 المستقبلون: {len(valid_users)} مستخدم

📝 الرسالة:
{message_text}

━━━━━━━━━━━━━━━
هل تريد إرسال هذا الإعلان؟"""

    keyboard = [
        [InlineKeyboardButton("✅ إرسال", callback_data="confirm_broadcast")],
        [InlineKeyboardButton("🔙 رجوع", callback_data="cancel_broadcast")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(preview_text, reply_markup=reply_markup)
    return BROADCAST_CONFIRM


async def handle_broadcast_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """معالجة تأكيد أو إلغاء البث"""
    import asyncio
    
    query = update.callback_query
    await query.answer()
    

    
    if query.data == "confirm_broadcast":
        broadcast_type = context.user_data.get('broadcast_type', 'all')
        message_text = context.user_data.get('broadcast_message', '')
        
        # التحقق من وجود الرسالة
        if not message_text:
            await query.edit_message_text("❌ خطأ: لم يتم العثور على رسالة البث. يرجى المحاولة مرة أخرى.")
            await restore_admin_keyboard(context, update.effective_chat.id)
            return ConversationHandler.END
        
        await query.edit_message_text("📤 جاري إرسال الإعلان...")
        
        success_count = 0
        failed_count = 0
        
        # فحص وجود صورة
        broadcast_photo = context.user_data.get('broadcast_photo')
        
        if broadcast_type == 'all':
            # إرسال للجميع
            all_users = db.execute_query("SELECT user_id FROM users")
            for user_tuple in all_users:
                user_id = user_tuple[0]
                try:
                    if broadcast_photo:
                        # إرسال صورة مع نص
                        await context.bot.send_photo(
                            chat_id=user_id,
                            photo=broadcast_photo,
                            caption=f"📢 إعلان هام\n\n{message_text}" if message_text else "📢 إعلان هام"
                        )
                    else:
                        # إرسال نص فقط
                        await context.bot.send_message(user_id, f"📢 إعلان هام\n\n{message_text}")
                    success_count += 1
                    # توقف قصير لتجنب حدود التيليجرام
                    await asyncio.sleep(0.05)
                except Exception as e:
                    failed_count += 1
                    print(f"فشل إرسال البث للمستخدم {user_id}: {e}")
        else:
            # إرسال للمستخدمين المخصصين
            valid_users = context.user_data.get('broadcast_valid_users', [])
            for user_id, name, original in valid_users:
                try:
                    if broadcast_photo:
                        # إرسال صورة مع نص
                        await context.bot.send_photo(
                            chat_id=user_id,
                            photo=broadcast_photo,
                            caption=f"📢 إعلان هام\n\n{message_text}" if message_text else "📢 إعلان هام"
                        )
                    else:
                        # إرسال نص فقط
                        await context.bot.send_message(user_id, f"📢 إعلان هام\n\n{message_text}")
                    success_count += 1
                except Exception as e:
                    failed_count += 1
                    print(f"فشل إرسال البث للمستخدم {user_id}: {e}")
        
        result_message = f"""✅ تم إرسال الإعلان

📊 الإحصائيات:
✅ نجح الإرسال: {success_count}
❌ فشل الإرسال: {failed_count}
📊 المجموع: {success_count + failed_count}"""

        await query.edit_message_text(result_message)
        
        # تنظيف البيانات المؤقتة
        broadcast_keys = ['broadcast_type', 'broadcast_message', 'broadcast_users_input', 'broadcast_valid_users']
        for key in broadcast_keys:
            context.user_data.pop(key, None)
        
        # إعادة تفعيل كيبورد الأدمن
        await restore_admin_keyboard(context, update.effective_chat.id, "📊 تم إرسال البث بنجاح")
            
    elif query.data == "cancel_broadcast":
        await query.edit_message_text("❌ تم إلغاء الإعلان.")
        
        # تنظيف البيانات المؤقتة
        broadcast_keys = ['broadcast_type', 'broadcast_message', 'broadcast_users_input', 'broadcast_valid_users']
        for key in broadcast_keys:
            context.user_data.pop(key, None)
        
        # إعادة تفعيل كيبورد الأدمن
        await restore_admin_keyboard(context, update.effective_chat.id)
    
    return ConversationHandler.END

async def handle_broadcast_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """بدء عملية البث"""
    # التحقق من صلاحيات الأدمن
    if not context.user_data.get('is_admin', False):
        await update.message.reply_text("❌ هذه الخدمة مخصصة للأدمن فقط!")
        return ConversationHandler.END
    
    keyboard = [
        [InlineKeyboardButton("📢 إرسال للجميع", callback_data="broadcast_all")],
        [InlineKeyboardButton("👥 إرسال لمستخدمين مخصصين", callback_data="broadcast_custom")],
        [InlineKeyboardButton("🔙 العودة", callback_data="back_to_admin")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "📢 قائمة البث\n\nاختر نوع الإرسال:",
        reply_markup=reply_markup
    )
    
    return BROADCAST_MESSAGE  # الانتقال لحالة انتظار اختيار نوع البث

async def handle_cancel_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """معالجة إلغاء البث"""
    query = update.callback_query
    await query.answer()
    
    # تنظيف البيانات المؤقتة مع الحفاظ على حالة الأدمن
    clean_user_data_preserve_admin(context)
    
    await query.edit_message_text("❌ تم إلغاء عملية البث")
    
    # إعادة تفعيل كيبورد الأدمن الرئيسي
    await restore_admin_keyboard(context, update.effective_chat.id, "🔧 لوحة الأدمن جاهزة للاستخدام")
    
    return ConversationHandler.END

# ===== معالج الأخطاء الشامل =====

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالج شامل للأخطاء"""
    logger.error(msg="Exception while handling an update:", exc_info=context.error)
    
    try:
        # تنظيف البيانات المؤقتة
        if hasattr(context, 'user_data') and context.user_data:
            clean_user_data_preserve_admin(context)
        
        # محاولة إرسال رسالة للمستخدم
        if update and hasattr(update, 'effective_chat') and update.effective_chat:
            try:
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="❌ حدث خطأ تقني. يرجى استخدام /start لإعادة تشغيل البوت",
                    reply_markup=ReplyKeyboardRemove()
                )
            except Exception as send_error:
                logger.error(f"Could not send error message: {send_error}")
        
        # تسجيل تفاصيل الخطأ
        if update and hasattr(update, 'effective_user'):
            user_id = update.effective_user.id
            try:
                db.log_action(user_id, "error_occurred", str(context.error))
            except Exception as log_error:
                logger.error(f"Could not log error: {log_error}")
        
    except Exception as handler_error:
        logger.error(f"Error in error handler: {handler_error}")

# ===== نظام مراقبة صحة البوت =====

class BotHealthMonitor:
    """نظام مراقبة صحة البوت"""
    
    def __init__(self):
        self.stuck_users: Dict[int, float] = {}  # user_id -> timestamp
        self.conversation_timeouts: Dict[int, float] = {}
        self.error_count: int = 0
        self.last_activity: float = time.time()
        
    def mark_user_activity(self, user_id: int):
        """تسجيل نشاط المستخدم"""
        self.stuck_users.pop(user_id, None)
        self.conversation_timeouts.pop(user_id, None)
        self.last_activity = time.time()
        
    def mark_user_stuck(self, user_id: int, conversation_state: str):
        """تسجيل مستخدم عالق"""
        self.stuck_users[user_id] = time.time()
        logger.warning(f"User {user_id} stuck in state: {conversation_state}")
        
    def mark_conversation_timeout(self, user_id: int):
        """تسجيل انتهاء مهلة المحادثة"""
        self.conversation_timeouts[user_id] = time.time()
        
    def increment_error(self):
        """زيادة عداد الأخطاء"""
        self.error_count += 1
        
    def get_stuck_users(self, timeout_minutes: int = 30) -> Set[int]:
        """الحصول على المستخدمين العالقين"""
        current_time = time.time()
        timeout_seconds = timeout_minutes * 60
        
        return {
            user_id for user_id, timestamp in self.stuck_users.items()
            if current_time - timestamp > timeout_seconds
        }
        
    def cleanup_stuck_users(self, timeout_minutes: int = 30):
        """تنظيف المستخدمين العالقين"""
        stuck_users = self.get_stuck_users(timeout_minutes)
        
        for user_id in stuck_users:
            try:
                db.log_action(user_id, "auto_unstuck", "System auto-cleanup")
                self.stuck_users.pop(user_id, None)
                logger.info(f"Auto-cleaned stuck user: {user_id}")
            except Exception as e:
                logger.error(f"Failed to cleanup stuck user {user_id}: {e}")
                
    def get_health_status(self) -> Dict:
        """الحصول على حالة صحة البوت"""
        return {
            "stuck_users_count": len(self.stuck_users),
            "timeout_conversations": len(self.conversation_timeouts),
            "error_count": self.error_count,
            "last_activity": datetime.fromtimestamp(self.last_activity),
            "uptime_minutes": (time.time() - self.last_activity) / 60
        }
    
    async def start_monitoring(self):
        """بدء مراقبة صحة البوت"""
        logger.info("Starting bot health monitoring...")
        
        # تشغيل روتين الفحص في الخلفية
        asyncio.create_task(health_check_routine())
        
        # تسجيل بداية المراقبة
        self.last_activity = time.time()
        logger.info("Bot health monitoring started successfully")

# إنشاء مراقب الصحة
# تم إزالة health_monitor لحل مشكلة تسجيل الخروج التلقائي

# تم إزالة دالة health_check_routine لحل مشكلة تسجيل الخروج التلقائي

async def initialize_cleanup_scheduler(application):
    """تهيئة جدولة التنظيف التلقائي"""
    try:
        # جدولة تنظيف العمليات المنتهية الصلاحية كل ساعة
        async def scheduled_cleanup():
            while True:
                await asyncio.sleep(3600)  # كل ساعة
                try:
                    logger.info("Running scheduled cleanup...")
                    await cleanup_old_orders()  # الدالة الموجودة مسبقاً
                    # تم إزالة health_monitor.cleanup_stuck_users()
                except Exception as e:
                    logger.error(f"Error in scheduled cleanup: {e}")
        
        # تشغيل التنظيف في الخلفية
        application.create_task(scheduled_cleanup())
        # تم إزالة مراقب الصحة
        logger.info("Cleanup scheduler and health monitor initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize cleanup scheduler: {e}")

def setup_bot():
    """إعداد البوت بدون تشغيله"""
    print("🔧 فحص إعدادات البوت...")
    
    if not TOKEN:
        print("❌ التوكن غير موجود!")
        print("يرجى إضافة التوكن في بداية الملف!")
        print("1. اذهب إلى @BotFather على تيليجرام")
        print("2. أنشئ بوت جديد وانسخ التوكن")
        print("3. ضع التوكن في متغير TOKEN في بداية الملف")
        return None
    
    print(f"✅ التوكن موجود: {TOKEN[:10]}...{TOKEN[-10:]}")
    print("🔧 بدء تهيئة البوت...")
    
    # تحميل الأسعار المحفوظة عند بدء التشغيل
    load_saved_prices()
    
    # تحميل معرف الأدمن من آخر تسجيل دخول ناجح
    try:
        global ADMIN_CHAT_ID
        admin_logs = db.execute_query("SELECT user_id FROM logs WHERE action = 'admin_login_success' ORDER BY timestamp DESC LIMIT 1")
        if admin_logs:
            ADMIN_CHAT_ID = admin_logs[0][0]
            print(f"✅ تم تحميل معرف الأدمن: {ADMIN_CHAT_ID}")
        else:
            print("⚠️ لم يتم العثور على تسجيل دخول أدمن سابق")
    except Exception as e:
        print(f"⚠️ خطأ في تحميل معرف الأدمن: {e}")
    
    # إنشاء ملفات المساعدة
    print("📁 إنشاء ملفات المساعدة...")
    create_requirements_file()
    create_readme_file()
    print("✅ تم إنشاء ملفات المساعدة")
    
    # إنشاء التطبيق
    print("⚡ إنشاء تطبيق التيليجرام...")
    try:
        application = Application.builder().token(TOKEN).build()
        print("✅ تم إنشاء التطبيق بنجاح")
        
        # اختبار الاتصال مع تيليجرام
        print("🌐 اختبار الاتصال مع خوادم تيليجرام...")
        print("🌐 سيتم اختبار الاتصال عند بدء التشغيل...")
        
    except Exception as e:
        print(f"❌ خطأ في إنشاء التطبيق أو الاتصال: {e}")
        return None
    
    # المعالجات ستتم إضافتها في setup_bot()
    
    print("📊 قاعدة البيانات جاهزة")
    print("⚡ البوت يعمل الآن!")
    print(f"🔑 التوكن: {TOKEN[:10]}...")
    print("💡 في انتظار الرسائل...")
    print("✅ البوت جاهز للتشغيل!")
    
    return application
    
    
async def handle_quantity_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """معالجة اختيار الكمية من قبل الأدمن"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "quantity_single":
        context.user_data["quantity"] = "5"
        # الانتقال لاختيار نوع البروكسي العادي
        keyboard = [
            [InlineKeyboardButton("Static ISP", callback_data="proxy_type_static_isp")],
            [InlineKeyboardButton("Static Residential", callback_data="proxy_type_static_residential")],
            [InlineKeyboardButton("🔙 رجوع", callback_data="cancel_processing")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # الحفاظ على المعلومات الأصلية مع إضافة سؤال نوع البروكسي
        original_message = context.user_data.get('original_order_message', '')
        combined_message = f"{original_message}\n\n━━━━━━━━━━━━━━━\n✅ تم قبول الدفع للطلب\n\n🆔 معرف الطلب: `{context.user_data['processing_order_id']}`\n📝 الطلب: بروكسي ستاتيك\n\n📋 الطلب جاهز للمعالجة والإرسال للمستخدم.\n\n━━━━━━━━━━━━━━━\n2️⃣ اختر نوع البروكسي:"
        
        await query.edit_message_text(
            combined_message,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
        return PROCESS_ORDER
        
    elif query.data == "quantity_package_socks":
        context.user_data["quantity"] = "10"
        
        # إرسال رسالة منفصلة لوضع الباكج مع زر إلغاء المعالجة
        package_keyboard = [
            [InlineKeyboardButton("🔙 رجوع", callback_data="cancel_processing")]
        ]
        package_reply_markup = InlineKeyboardMarkup(package_keyboard)
        
        package_instruction_message = f"""📦 **وضع الباكج**

🆔 معرف الطلب: `{context.user_data['processing_order_id']}`
📝 نوع الطلب: باكج

━━━━━━━━━━━━━━━
يرجى كتابة الرسالة المخصصة التي تريد إرسالها للمستخدم:

💡 يمكنك تضمين جميع تفاصيل البروكسي في رسالة واحدة
💡 الرسالة ستُرسل كما تكتبها بدون تعديل
💡 يمكنك استخدام أي تنسيق تريده"""
        
        # إرسال رسالة منفصلة للباكج
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=package_instruction_message,
            reply_markup=package_reply_markup,
            parse_mode="Markdown"
        )
        
        # تحديث الرسالة الأصلية لإبقاء زر العودة لاختيار الكمية
        original_keyboard = [
            [InlineKeyboardButton("🔙 العودة لاختيار الكمية", callback_data="back_to_quantity")]
        ]
        original_reply_markup = InlineKeyboardMarkup(original_keyboard)
        
        # الحفاظ على المعلومات الأصلية مع تحديث الحالة
        original_message = context.user_data.get('original_order_message', '')
        updated_message = f"{original_message}\n\n━━━━━━━━━━━━━━━\n✅ تم قبول الدفع للطلب\n📝 الطلب: باكج\n📋 الطلب جاهز للمعالجة والإرسال للمستخدم"
        
        await query.edit_message_text(
            updated_message,
            reply_markup=original_reply_markup,
            parse_mode="Markdown"
        )
        return PACKAGE_MESSAGE

async def handle_package_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """معالجة رسالة الباكج المخصصة"""
    if update.message and update.message.text:
        package_message = update.message.text
        context.user_data["package_message"] = package_message
        
        # عرض معاينة الرسالة مع خيارات التأكيد
        await show_package_preview_confirmation(update, context, package_message)
        return PACKAGE_CONFIRMATION
    
    return PACKAGE_MESSAGE

async def show_package_preview_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE, package_message: str) -> None:
    """عرض معاينة رسالة الباكج مع خيارات التأكيد"""
    order_id = context.user_data.get("processing_order_id", "غير معروف")
    
    preview_message = f"""📋 **معاينة رسالة الباكج**

🆔 معرف الطلب: {order_id}
📦 نوع الطلب: باكج

━━━━━━━━━━━━━━━
**الرسالة التي ستُرسل للمستخدم:**

{package_message}
━━━━━━━━━━━━━━━

❓ هل تريد إرسال هذه الرسالة للمستخدم وإتمام الطلب؟"""
    
    keyboard = [
        [InlineKeyboardButton("✅ إرسال وإتمام الطلب", callback_data="confirm_send_package")],
        [InlineKeyboardButton("❌ لا", callback_data="decline_send_package")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        preview_message,
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def handle_package_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """معالجة تأكيد إرسال الباكج"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "confirm_send_package":
        # إرسال الباكج للمستخدم وإتمام الطلب
        package_message = context.user_data.get("package_message", "")
        await send_package_to_user_from_confirmation(query, context, package_message)
        return ConversationHandler.END
        
    elif query.data == "decline_send_package":
        # عرض خيارات ماذا تريد أن تفعل
        await show_package_action_choices(query, context)
        return PACKAGE_ACTION_CHOICE
    
    return PACKAGE_CONFIRMATION

async def show_package_action_choices(query, context: ContextTypes.DEFAULT_TYPE) -> None:
    """عرض خيارات العمل بعد رفض إرسال الباكج"""
    message = """❓ **ماذا تريد أن تفعل؟**

يمكنك اختيار أحد الخيارات التالية:"""
    
    keyboard = [
        [InlineKeyboardButton("🔄 إعادة تصميم الباكج", callback_data="redesign_package")],
        [InlineKeyboardButton("📋 مراجعة الطلب لاحقاً", callback_data="review_later")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        message,
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def handle_package_action_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """معالجة اختيار العمل بعد رفض الباكج"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "redesign_package":
        # إرسال رسالة منفصلة لإعادة تصميم الباكج
        package_keyboard = [
            [InlineKeyboardButton("🔙 رجوع", callback_data="cancel_processing")]
        ]
        package_reply_markup = InlineKeyboardMarkup(package_keyboard)
        
        redesign_message = f"""📦 **إعادة تصميم الباكج**

🆔 معرف الطلب: `{context.user_data['processing_order_id']}`

━━━━━━━━━━━━━━━
يرجى كتابة الرسالة المخصصة الجديدة التي تريد إرسالها للمستخدم:

💡 يمكنك تضمين جميع تفاصيل البروكسي في رسالة واحدة
💡 الرسالة ستُرسل كما تكتبها بدون تعديل
💡 يمكنك استخدام أي تنسيق تريده"""
        
        # إرسال رسالة منفصلة لإعادة التصميم
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=redesign_message,
            reply_markup=package_reply_markup,
            parse_mode="Markdown"
        )
        
        # حذف رسالة المعاينة السابقة
        await query.delete_message()
        
        return PACKAGE_MESSAGE
        
    elif query.data == "review_later":
        # الخروج من الحلقة دون تصنيف الطلب
        order_id = context.user_data.get("processing_order_id", "غير معروف")
        
        await query.edit_message_text(
            f"📋 **مراجعة لاحقاً**\n\n🆔 معرف الطلب: {order_id}\n\n✅ تم الخروج من معالجة الطلب\n❗ الطلب لا يزال في حالة معلق ويمكن معالجته لاحقاً\n\n💡 لن يتم تصنيف الطلب كناجح أو فاشل",
            parse_mode="Markdown"
        )
        
        # تنظيف البيانات المؤقتة مع الحفاظ على حالة الأدمن
        clean_user_data_preserve_admin(context)
        await restore_admin_keyboard(context, update.effective_chat.id, "🔧 لوحة الأدمن جاهزة للاستخدام")
        
        return ConversationHandler.END
    
    return PACKAGE_ACTION_CHOICE

async def send_package_to_user_from_confirmation(query, context: ContextTypes.DEFAULT_TYPE, package_message: str) -> None:
    """إرسال الباكج للمستخدم من صفحة التأكيد"""
    order_id = context.user_data.get("processing_order_id", "")
    
    # الحصول على معلومات المستخدم والطلب
    user_query = """
        SELECT o.user_id, u.first_name, u.last_name 
        FROM orders o 
        JOIN users u ON o.user_id = u.user_id 
        WHERE o.id = ?
    """
    user_result = db.execute_query(user_query, (order_id,))
    
    if user_result:
        user_id, first_name, last_name = user_result[0]
        user_full_name = f"{first_name} {last_name or ''}".strip()
        
        # إرسال الباكج للمستخدم
        final_message = f"""✅ تم معالجة طلب {user_full_name}

🆔 معرف الطلب: {order_id}
📦 نوع الطلب: باكج

━━━━━━━━━━━━━━━
{package_message}
━━━━━━━━━━━━━━━

📅 التاريخ: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}"""
        
        await context.bot.send_message(user_id, final_message, parse_mode="Markdown")
        
        # تحديث حالة الطلب
        db.execute_query(
            "UPDATE orders SET status = 'completed', processed_at = CURRENT_TIMESTAMP, proxy_details = ?, truly_processed = TRUE WHERE id = ?",
            (package_message, order_id)
        )
        
        # التحقق من إضافة رصيد الإحالة لأول عملية شراء
        await check_and_add_referral_bonus(context, user_id, order_id)
        
        # رسالة تأكيد للأدمن
        admin_message = f"""✅ **تم إرسال الباكج بنجاح وإتمام الطلب**

👤 المستخدم: {user_full_name}
🆔 معرف الطلب: {order_id}
📦 نوع الطلب: باكج

📝 الرسالة المرسلة:
{package_message}

🎉 تم تصنيف الطلب كناجح ونقله للطلبات المكتملة"""

        await query.edit_message_text(admin_message, parse_mode="Markdown")
        
        # تنظيف البيانات المؤقتة مع الحفاظ على حالة الأدمن
        clean_user_data_preserve_admin(context)
        await restore_admin_keyboard(context, query.message.chat_id, "🔧 لوحة الأدمن جاهزة للاستخدام")

async def handle_back_to_quantity(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """معالجة العودة لاختيار الكمية"""
    query = update.callback_query
    await query.answer()
    
    # تحديد لغة الأدمن (افتراضياً العربية للأدمن)
    admin_language = get_user_language(query.from_user.id)
    
    # إعادة عرض خيارات الكمية
    if admin_language == 'ar':
        keyboard = [
            [InlineKeyboardButton("📦باكج 5", callback_data="quantity_single")],
            [InlineKeyboardButton("📦10 باكج", callback_data="quantity_package")],
            [InlineKeyboardButton("🔙 رجوع", callback_data="cancel_processing")]
        ]
        quantity_text = "1️⃣ اختر الكمية المطلوبة:"
    else:
        keyboard = [
            [InlineKeyboardButton("📦 Package 5", callback_data="quantity_single")],
            [InlineKeyboardButton("📦 Package 10", callback_data="quantity_package")],
            [InlineKeyboardButton("🔙 Back Processing", callback_data="cancel_processing")]
        ]
        quantity_text = "1️⃣ Choose the required quantity:"
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        quantity_text,
        reply_markup=reply_markup
    )
    
    return ENTER_PROXY_QUANTITY

async def handle_proxy_quantity(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """معالجة إدخال كمية البروكسيات"""
    user_id = update.effective_user.id
    language = get_user_language(user_id)
    
    try:
        quantity_text = update.message.text.strip()
        
        # التحقق من أن النص يحتوي على رقم صحيح فقط
        if not quantity_text.isdigit():
            await update.message.reply_text(MESSAGES[language]['invalid_quantity'], parse_mode='Markdown')
            return ENTER_PROXY_QUANTITY
        
        quantity = int(quantity_text)
        
        # التحقق من أن العدد بين 1 و 100
        if quantity < 1 or quantity > 100:
            await update.message.reply_text(MESSAGES[language]['invalid_quantity'], parse_mode='Markdown')
            return ENTER_PROXY_QUANTITY
        
        # حفظ الكمية
        context.user_data['quantity'] = quantity
        
        # إنشاء الطلب مباشرة بدون طرق الدفع
        try:
            # محاولة إنشاء الطلب مباشرة
            user_id = update.effective_user.id
            order_id = await create_order_directly_from_message(update, context, language)
            
            # إرسال رسالة تأكيد
            if language == 'ar':
                success_message = f"""✅ تم إرسال طلبك بنجاح!

🆔 معرف الطلب: {order_id}
⏰ سيتم مراجعة طلبك من قبل الإدارة وإرسال البيانات قريباً

📞 للاستفسار عن الطلب تواصل مع الدعم"""
            else:
                success_message = f"""✅ Your order has been sent successfully!

🆔 Order ID: {order_id}
⏰ Your order will be reviewed by management and data sent soon

📞 For inquiry contact support"""
            
            await update.message.reply_text(success_message, parse_mode='Markdown')
            return ConversationHandler.END
            
        except Exception as order_error:
            logger.error(f"Error creating order from message: {order_error}")
            await update.message.reply_text(
                "❌ حدث خطأ في إنشاء الطلب. يرجى المحاولة مرة أخرى أو التواصل مع الدعم.",
                parse_mode='Markdown'
            )
            return ConversationHandler.END
        
    except Exception as e:
        logger.error(f"Error in handle_proxy_quantity: {e}")
        await update.message.reply_text(MESSAGES[language]['invalid_quantity'], parse_mode='Markdown')
        return ENTER_PROXY_QUANTITY

async def handle_edit_services_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """بدء تعديل رسالة الخدمات - طلب النص العربي أولاً"""
    if not context.user_data.get('is_admin'):
        return ConversationHandler.END
    
    keyboard = [[KeyboardButton("🔙 رجوع")]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        "📝 **خطوة 1 من 2**\n\nأدخل رسالة الخدمات بالعربية:\n\n💡 يمكنك استخدام تنسيق Markdown للتنسيق",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    return EDIT_SERVICES_MESSAGE_AR

async def handle_services_message_ar_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """معالجة إدخال رسالة الخدمات العربية"""
    if not context.user_data.get('is_admin'):
        return ConversationHandler.END
    
    if update.message.text == "🔙 رجوع":
        await handle_admin_settings_menu(update, context)
        return ConversationHandler.END
    
    # حفظ النص العربي مؤقتاً
    context.user_data['temp_services_ar'] = update.message.text
    
    await update.message.reply_text(
        "✅ تم حفظ النص العربي!\n\n📝 **خطوة 2 من 2**\n\nالآن أدخل رسالة الخدمات بالإنجليزية:\n\n💡 يمكنك استخدام تنسيق Markdown للتنسيق",
        parse_mode='Markdown'
    )
    return EDIT_SERVICES_MESSAGE_EN

async def handle_services_message_en_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """معالجة إدخال رسالة الخدمات الإنجليزية وحفظ كلا النصين"""
    if not context.user_data.get('is_admin'):
        return ConversationHandler.END
    
    if update.message.text == "🔙 رجوع":
        await handle_admin_settings_menu(update, context)
        return ConversationHandler.END
    
    ar_message = context.user_data.get('temp_services_ar', '')
    en_message = update.message.text
    
    # حفظ الرسالتين للغتين
    try:
        db.execute_query("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", ('services_message_ar', ar_message))
        db.execute_query("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", ('services_message_en', en_message))
        
        await update.message.reply_text(
            f"✅ تم تحديث رسالة الخدمات بنجاح للغتين!\n\n🇸🇦 **النص العربي:**\n{ar_message}\n\n🇺🇸 **النص الإنجليزي:**\n{en_message}",
            parse_mode='Markdown'
        )
    except Exception as e:
        logger.error(f"Error saving services message: {e}")
        await update.message.reply_text(
            "❌ حدث خطأ في حفظ الرسالة. يرجى المحاولة مرة أخرى."
        )
    
    # تنظيف البيانات المؤقتة
    context.user_data.pop('temp_services_ar', None)
    
    # إعادة تفعيل كيبورد الأدمن
    await handle_admin_settings_menu(update, context)
    return ConversationHandler.END

# معالج معالجة الطلبات للأدمن
process_order_conv_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(handle_process_order, pattern="^process_")],
    states={
        PROCESS_ORDER: [
            CallbackQueryHandler(handle_payment_success, pattern="^payment_success$"),
            CallbackQueryHandler(handle_payment_failed, pattern="^payment_failed$"),
            CallbackQueryHandler(handle_quantity_selection, pattern="^quantity_"),
            CallbackQueryHandler(handle_proxy_details_input, pattern="^proxy_type_"),
            CallbackQueryHandler(handle_back_to_quantity, pattern="^back_to_quantity$"),
            CallbackQueryHandler(handle_cancel_processing, pattern="^cancel_processing$"),
            # معالج الرسائل النصية عندما ينتظر البوت رسالة الأدمن
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_admin_message_for_proxy)
        ],
        ENTER_PROXY_TYPE: [
            CallbackQueryHandler(handle_proxy_details_input, pattern="^proxy_type_"),
            CallbackQueryHandler(handle_cancel_processing, pattern="^cancel_processing$")
        ],
        ENTER_PROXY_ADDRESS: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_proxy_details_input),
            CallbackQueryHandler(handle_cancel_proxy_setup, pattern="^cancel_proxy_setup$"),
            CallbackQueryHandler(handle_cancel_processing, pattern="^cancel_processing$")
        ],
        ENTER_PROXY_PORT: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_proxy_details_input),
            CallbackQueryHandler(handle_cancel_proxy_setup, pattern="^cancel_proxy_setup$"),
            CallbackQueryHandler(handle_cancel_processing, pattern="^cancel_processing$")
        ],
        ENTER_COUNTRY: [
            CallbackQueryHandler(handle_admin_country_selection, pattern="^admin_country_"),
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_proxy_details_input),
            CallbackQueryHandler(handle_cancel_proxy_setup, pattern="^cancel_proxy_setup$"),
            CallbackQueryHandler(handle_cancel_processing, pattern="^cancel_processing$")
        ],
        ENTER_STATE: [
            CallbackQueryHandler(handle_admin_country_selection, pattern="^admin_state_"),
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_proxy_details_input),
            CallbackQueryHandler(handle_cancel_proxy_setup, pattern="^cancel_proxy_setup$"),
            CallbackQueryHandler(handle_cancel_processing, pattern="^cancel_processing$")
        ],
        ENTER_USERNAME: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_proxy_details_input),
            CallbackQueryHandler(handle_cancel_proxy_setup, pattern="^cancel_proxy_setup$"),
            CallbackQueryHandler(handle_cancel_processing, pattern="^cancel_processing$")
        ],
        ENTER_PASSWORD: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_proxy_details_input),
            CallbackQueryHandler(handle_cancel_proxy_setup, pattern="^cancel_proxy_setup$"),
            CallbackQueryHandler(handle_cancel_processing, pattern="^cancel_processing$")
        ],
        ENTER_THANK_MESSAGE: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_proxy_details_input),
            CallbackQueryHandler(handle_cancel_proxy_setup, pattern="^cancel_proxy_setup$"),
            CallbackQueryHandler(handle_order_completed_success, pattern="^order_completed_success$"),
            CallbackQueryHandler(handle_cancel_processing, pattern="^cancel_processing$")
        ],
        CUSTOM_MESSAGE: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_admin_message_for_proxy),
            CallbackQueryHandler(handle_custom_message_choice, pattern="^(send_custom_message|no_custom_message|send_custom_message_failed|no_custom_message_failed)$"),
            CallbackQueryHandler(handle_cancel_custom_message, pattern="^cancel_custom_message$"),
            CallbackQueryHandler(handle_cancel_processing, pattern="^cancel_processing$")
        ],
        PACKAGE_MESSAGE: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_package_message),
            CallbackQueryHandler(handle_cancel_processing, pattern="^cancel_processing$"),
            CallbackQueryHandler(handle_back_to_quantity, pattern="^back_to_quantity$")
        ],
        PACKAGE_CONFIRMATION: [
            CallbackQueryHandler(handle_package_confirmation, pattern="^(confirm_send_package|decline_send_package)$"),
            CallbackQueryHandler(handle_cancel_processing, pattern="^cancel_processing$")
        ],
        PACKAGE_ACTION_CHOICE: [
            CallbackQueryHandler(handle_package_action_choice, pattern="^(redesign_package|review_later)$"),
            CallbackQueryHandler(handle_cancel_processing, pattern="^cancel_processing$")
        ]
    },
    fallbacks=[
        # الأوامر الأساسية
        CommandHandler("start", start),
        CommandHandler("cancel", lambda u, c: ConversationHandler.END),
        CommandHandler("reset", handle_reset_command),
        CommandHandler("cleanup", handle_cleanup_command),
        CommandHandler("help", help_command),
        # معالجة كلمات الإلغاء
        MessageHandler(filters.Regex("^(إلغاء|cancel|خروج|exit|stop)$"), handle_stuck_conversation),
        # معالجة أي callback query غير متوقع
        CallbackQueryHandler(handle_stuck_conversation),
        # معالجة أي رسالة نصية أو أمر غير متوقع
        MessageHandler(filters.TEXT | filters.COMMAND, handle_stuck_conversation),
        # معالجة الملفات والوسائط غير المرغوبة
        MessageHandler(filters.PHOTO | filters.VIDEO | filters.Document.ALL | filters.AUDIO, handle_stuck_conversation)
    ]
)

# معالج تغيير كلمة المرور
password_change_conv_handler = ConversationHandler(
    entry_points=[MessageHandler(filters.Regex("^🔐 تغيير كلمة المرور$"), change_admin_password)],
    states={
        ADMIN_LOGIN: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_password_change),
            CallbackQueryHandler(handle_cancel_password_change, pattern="^cancel_password_change$")
        ],
    },
    fallbacks=[
        # الأوامر الأساسية
        CommandHandler("start", start),
        CommandHandler("cancel", lambda u, c: ConversationHandler.END),
        CommandHandler("reset", handle_reset_command),
        CommandHandler("cleanup", handle_cleanup_command),
        CommandHandler("help", help_command),
        # معالجة كلمات الإلغاء
        MessageHandler(filters.Regex("^(إلغاء|cancel|خروج|exit|stop)$"), handle_stuck_conversation),
        # معالجة أي callback query غير متوقع
        CallbackQueryHandler(handle_stuck_conversation),
        # معالجة أي رسالة نصية أو أمر غير متوقع
        MessageHandler(filters.TEXT | filters.COMMAND, handle_stuck_conversation),
        # معالجة الملفات والوسائط غير المرغوبة
        MessageHandler(filters.PHOTO | filters.VIDEO | filters.Document.ALL | filters.AUDIO, handle_stuck_conversation)
    ]
)

# Callback handlers لأزرار السوكس الجديدة
async def handle_socks_price_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Callback handler لأزرار أسعار السوكس"""
    query = update.callback_query
    await query.answer()
    
    # تحديد العملية بناءً على callback_data
    if query.data == "set_socks_single":
        return await set_socks_single_price(update, context)
    elif query.data == "set_socks_double":
        return await set_socks_double_price(update, context)
    elif query.data == "set_socks_package5":
        return await set_socks_package5_price(update, context)
    elif query.data == "set_socks_package10":
        return await set_socks_package10_price(update, context)
    elif query.data == "back_to_prices_menu":
        # الرجوع إلى قائمة إدارة الأسعار
        await manage_prices_menu(update, context)
        return ConversationHandler.END
    
    return ConversationHandler.END

    # معالج شامل لجميع وظائف الأدمن
admin_functions_conv_handler = ConversationHandler(
    entry_points=[
        MessageHandler(filters.Regex("^🔍 استعلام عن مستخدم$"), handle_admin_user_lookup),
        MessageHandler(filters.Regex("^🗑️ تصفير رصيد مستخدم$"), reset_user_balance),
        MessageHandler(filters.Regex("^💵 تحديد قيمة الإحالة$"), set_referral_amount),
        MessageHandler(filters.Regex("^💰 تعديل سعر النقطة$"), set_credit_price),
        MessageHandler(filters.Regex("^💰 تعديل أسعار ستاتيك$"), set_static_prices),
        MessageHandler(filters.Regex("^💰 تعديل أسعار سوكس$"), set_socks_prices),
        MessageHandler(filters.Regex("^🔍 الاستعلام عن طلب$"), admin_order_inquiry),
        MessageHandler(filters.Regex("^🔕 ساعات الهدوء$"), set_quiet_hours),
        MessageHandler(filters.Regex("^🗑️ حذف جميع الطلبات$"), delete_all_orders),
        # إضافة callback handlers لأسعار السوكس
        CallbackQueryHandler(handle_socks_price_callback, pattern="^(set_socks_single|set_socks_double|set_socks_package5|set_socks_package10|back_to_prices_menu)$")
    ],
    states={
        USER_LOOKUP: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_user_lookup_unified),
            CallbackQueryHandler(handle_cancel_user_lookup, pattern="^cancel_user_lookup$"),
            CallbackQueryHandler(handle_cancel_balance_reset, pattern="^cancel_balance_reset$")
        ],
        REFERRAL_AMOUNT: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_referral_amount_update),
            CallbackQueryHandler(handle_cancel_referral_amount, pattern="^cancel_referral_amount$")
        ],
        SET_PRICE_STATIC: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_static_price_update),
            CallbackQueryHandler(handle_cancel_static_prices, pattern="^cancel_static_prices$"),
            CallbackQueryHandler(handle_set_price_isp, pattern="^set_price_isp$"),
            CallbackQueryHandler(handle_set_price_verizon, pattern="^set_price_verizon$"),
            CallbackQueryHandler(handle_set_price_residential_2, pattern="^set_price_residential_2$"),
            CallbackQueryHandler(handle_set_price_datacenter, pattern="^set_price_datacenter$"),
            CallbackQueryHandler(handle_set_price_weekly, pattern="^set_price_weekly$")
        ],
        SET_PRICE_ISP_ATT: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_individual_static_price_update),
            CallbackQueryHandler(handle_cancel_static_prices, pattern="^cancel_static_prices$")
        ],
        SET_PRICE_VERIZON: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_individual_static_price_update),
            CallbackQueryHandler(handle_cancel_static_prices, pattern="^cancel_static_prices$")
        ],
        SET_PRICE_RESIDENTIAL_2: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_individual_static_price_update),
            CallbackQueryHandler(handle_cancel_static_prices, pattern="^cancel_static_prices$")
        ],
        SET_PRICE_DAILY: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_individual_static_price_update),
            CallbackQueryHandler(handle_cancel_static_prices, pattern="^cancel_static_prices$")
        ],
        SET_PRICE_WEEKLY: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_individual_static_price_update),
            CallbackQueryHandler(handle_cancel_static_prices, pattern="^cancel_static_prices$")
        ],
        SET_PRICE_SOCKS: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_socks_price_update),
            CallbackQueryHandler(handle_cancel_socks_prices, pattern="^cancel_socks_prices$"),
            CallbackQueryHandler(handle_socks_price_callback, pattern="^(set_socks_single|set_socks_double|set_socks_package5|set_socks_package10)$")
        ],
        SET_POINT_PRICE: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_credit_price_update),
            CallbackQueryHandler(handle_cancel_credit_price, pattern="^cancel_credit_price$")
        ],
        ADMIN_ORDER_INQUIRY: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_order_inquiry),
            CallbackQueryHandler(handle_cancel_order_inquiry, pattern="^cancel_order_inquiry$")
        ],
        QUIET_HOURS: [CallbackQueryHandler(handle_quiet_hours_selection, pattern="^quiet_")],
        CONFIRM_DELETE_ALL_ORDERS: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_confirm_delete_all_orders)
        ]
    },
    fallbacks=[
        # الأوامر الأساسية
        CommandHandler("start", start),
        CommandHandler("cancel", lambda u, c: ConversationHandler.END),
        CommandHandler("reset", handle_reset_command),
        CommandHandler("cleanup", handle_cleanup_command),
        CommandHandler("help", help_command),
        # معالجة كلمات الإلغاء
        MessageHandler(filters.Regex("^(إلغاء|cancel|خروج|exit|stop)$"), handle_stuck_conversation),
        # معالجة أي callback query غير متوقع
        CallbackQueryHandler(handle_stuck_conversation),
        # معالجة أي رسالة نصية أو أمر غير متوقع
        MessageHandler(filters.TEXT | filters.COMMAND, handle_stuck_conversation),
        # معالجة الملفات والوسائط غير المرغوبة
        MessageHandler(filters.PHOTO | filters.VIDEO | filters.Document.ALL | filters.AUDIO, handle_stuck_conversation)
    ]
)

admin_conv_handler = ConversationHandler(
    entry_points=[CommandHandler("admin_login", admin_login)],
    states={
        ADMIN_LOGIN: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_admin_password)],
        ADMIN_MENU: [CallbackQueryHandler(handle_admin_menu_actions)],
        USER_LOOKUP: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_user_lookup_unified),
            CallbackQueryHandler(handle_cancel_user_lookup, pattern="^cancel_user_lookup$")
        ]
    },
    fallbacks=[
        # الأوامر الأساسية
        CommandHandler("start", start),
        CommandHandler("cancel", lambda u, c: ConversationHandler.END),
        CommandHandler("reset", handle_reset_command),
        CommandHandler("cleanup", handle_cleanup_command),
        CommandHandler("help", help_command),
        # معالجة كلمات الإلغاء
        MessageHandler(filters.Regex("^(إلغاء|cancel|خروج|exit|stop)$"), handle_stuck_conversation),
        # معالجة أي callback query غير متوقع
        CallbackQueryHandler(handle_stuck_conversation),
        # معالجة أي رسالة نصية أو أمر غير متوقع
        MessageHandler(filters.TEXT | filters.COMMAND, handle_stuck_conversation),
        # معالجة الملفات والوسائط غير المرغوبة
        MessageHandler(filters.PHOTO | filters.VIDEO | filters.Document.ALL | filters.AUDIO, handle_stuck_conversation)
    ]
)
    
    # معالج إثبات الدفع
payment_conv_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(handle_payment_method_selection, pattern="^payment_")],
    states={
        ENTER_PROXY_QUANTITY: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_proxy_quantity),
            CallbackQueryHandler(handle_cancel_payment_proof, pattern="^cancel_payment_proof$")
        ],
        PAYMENT_PROOF: [
            MessageHandler(filters.ALL & ~filters.COMMAND, handle_payment_proof),
            CallbackQueryHandler(handle_cancel_payment_proof, pattern="^cancel_payment_proof$")
        ],
    },
    fallbacks=[
        # الأوامر الأساسية
        CommandHandler("start", start),
        CommandHandler("cancel", lambda u, c: ConversationHandler.END),
        CommandHandler("reset", handle_reset_command),
        CommandHandler("cleanup", handle_cleanup_command),
        CommandHandler("help", help_command),
        # معالجة كلمات الإلغاء
        MessageHandler(filters.Regex("^(إلغاء|cancel|خروج|exit|stop)$"), handle_stuck_conversation),
        # معالجة أي callback query غير متوقع
        CallbackQueryHandler(handle_stuck_conversation),
        # معالجة أي رسالة نصية أو أمر غير متوقع
        MessageHandler(filters.TEXT | filters.COMMAND, handle_stuck_conversation),
        # معالجة الملفات والوسائط غير المرغوبة
        MessageHandler(filters.PHOTO | filters.VIDEO | filters.Document.ALL | filters.AUDIO, handle_stuck_conversation)
    ]
)
    
    # معالج البث
broadcast_conv_handler = ConversationHandler(
    entry_points=[
        MessageHandler(filters.Regex("^📢 البث$"), handle_broadcast_start),
        CallbackQueryHandler(handle_broadcast_selection, pattern="^(broadcast_all|broadcast_custom)$")
    ],
    states={
        BROADCAST_MESSAGE: [
            CallbackQueryHandler(handle_broadcast_selection, pattern="^(broadcast_all|broadcast_custom)$"),
            MessageHandler((filters.TEXT & ~filters.COMMAND) | filters.PHOTO, handle_broadcast_message),
            CallbackQueryHandler(handle_cancel_broadcast, pattern="^cancel_broadcast$")
        ],
        BROADCAST_USERS: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_broadcast_users),
            CallbackQueryHandler(handle_cancel_broadcast, pattern="^cancel_broadcast$")
        ],
        BROADCAST_CONFIRM: [CallbackQueryHandler(handle_broadcast_confirmation, pattern="^(confirm_broadcast|cancel_broadcast)$")],

    },
    fallbacks=[
        # الأوامر الأساسية
        CommandHandler("start", start),
        CommandHandler("cancel", lambda u, c: ConversationHandler.END),
        CommandHandler("reset", handle_reset_command),
        CommandHandler("cleanup", handle_cleanup_command),
        CommandHandler("help", help_command),
        # معالجة كلمات الإلغاء
        MessageHandler(filters.Regex("^(إلغاء|cancel|خروج|exit|stop)$"), handle_stuck_conversation),
        # معالجة أي callback query غير متوقع
        CallbackQueryHandler(handle_stuck_conversation),
        # معالجة أي رسالة نصية أو أمر غير متوقع
        MessageHandler(filters.TEXT | filters.COMMAND, handle_stuck_conversation),
        # معالجة الملفات والوسائط غير المرغوبة
        MessageHandler(filters.PHOTO | filters.VIDEO | filters.Document.ALL | filters.AUDIO, handle_stuck_conversation)
    ]
)

# معالج تعديل رسالة الخدمات
services_message_conv_handler = ConversationHandler(
    entry_points=[MessageHandler(filters.Regex("^📝 تعديل رسالة الخدمات$"), handle_edit_services_message)],
    states={
        EDIT_SERVICES_MESSAGE_AR: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_services_message_ar_input),
        ],
        EDIT_SERVICES_MESSAGE_EN: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_services_message_en_input),
        ],
    },
    fallbacks=[
        CommandHandler("start", start),
        CommandHandler("cancel", lambda u, c: ConversationHandler.END),
        CommandHandler("reset", handle_reset_command),
        MessageHandler(filters.Regex("^(🔙 رجوع|🔙 Back)$"), lambda u, c: ConversationHandler.END),
        CallbackQueryHandler(lambda u, c: ConversationHandler.END),
        MessageHandler(filters.TEXT | filters.COMMAND, lambda u, c: ConversationHandler.END),
    ],
    per_message=False
)

async def handle_edit_exchange_rate_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """بدء تعديل رسالة سعر الصرف - طلب النص العربي أولاً"""
    if not context.user_data.get('is_admin'):
        return ConversationHandler.END
    
    keyboard = [[KeyboardButton("🔙 رجوع")]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        "📝 **خطوة 1 من 2**\n\nأدخل رسالة سعر الصرف بالعربية:\n\n💡 يمكنك استخدام تنسيق Markdown للتنسيق",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    return EDIT_EXCHANGE_RATE_MESSAGE_AR


async def handle_exchange_rate_message_ar_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """معالجة إدخال رسالة سعر الصرف العربية"""
    if not context.user_data.get('is_admin'):
        return ConversationHandler.END
    
    if update.message.text == "🔙 رجوع":
        await handle_admin_settings_menu(update, context)
        return ConversationHandler.END
    
    # حفظ النص العربي مؤقتاً
    context.user_data['temp_exchange_ar'] = update.message.text
    
    await update.message.reply_text(
        "✅ تم حفظ النص العربي!\n\n📝 **خطوة 2 من 2**\n\nالآن أدخل رسالة سعر الصرف بالإنجليزية:\n\n💡 يمكنك استخدام تنسيق Markdown للتنسيق",
        parse_mode='Markdown'
    )
    return EDIT_EXCHANGE_RATE_MESSAGE_EN

async def handle_exchange_rate_message_en_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """معالجة إدخال رسالة سعر الصرف الإنجليزية وحفظ كلا النصين"""
    if not context.user_data.get('is_admin'):
        return ConversationHandler.END
    
    if update.message.text == "🔙 رجوع":
        await handle_admin_settings_menu(update, context)
        return ConversationHandler.END
    
    ar_message = context.user_data.get('temp_exchange_ar', '')
    en_message = update.message.text
    
    # حفظ الرسالتين للغتين
    try:
        db.execute_query("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", ('exchange_rate_message_ar', ar_message))
        db.execute_query("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", ('exchange_rate_message_en', en_message))
        
        await update.message.reply_text(
            f"✅ تم تحديث رسالة سعر الصرف بنجاح للغتين!\n\n🇸🇦 **النص العربي:**\n{ar_message}\n\n🇺🇸 **النص الإنجليزي:**\n{en_message}",
            parse_mode='Markdown'
        )
    except Exception as e:
        logger.error(f"Error saving exchange rate message: {e}")
        await update.message.reply_text(
            "❌ حدث خطأ في حفظ الرسالة. يرجى المحاولة مرة أخرى."
        )
    
    # تنظيف البيانات المؤقتة
    context.user_data.pop('temp_exchange_ar', None)
    
    # إعادة تفعيل كيبورد الأدمن
    await handle_admin_settings_menu(update, context)
    return ConversationHandler.END


# معالج تعديل رسالة سعر الصرف
exchange_rate_message_conv_handler = ConversationHandler(
    entry_points=[MessageHandler(filters.Regex("^💱 تعديل رسالة سعر الصرف$"), handle_edit_exchange_rate_message)],
    states={
        EDIT_EXCHANGE_RATE_MESSAGE_AR: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_exchange_rate_message_ar_input),
        ],
        EDIT_EXCHANGE_RATE_MESSAGE_EN: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_exchange_rate_message_en_input),
        ],
    },
    fallbacks=[
        CommandHandler("start", start),
        CommandHandler("cancel", lambda u, c: ConversationHandler.END),
        CommandHandler("reset", handle_reset_command),
        MessageHandler(filters.Regex("^(🔙 رجوع|🔙 Back)$"), lambda u, c: ConversationHandler.END),
        CallbackQueryHandler(lambda u, c: ConversationHandler.END),
        MessageHandler(filters.TEXT | filters.COMMAND, lambda u, c: ConversationHandler.END),
    ],
    per_message=False
)

# ===== معالج الأخطاء الشامل =====
async def global_error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالج شامل لجميع الأخطاء غير المتوقعة"""
    try:
        user_id = None
        error_context = "unknown"
        
        # محاولة الحصول على معرف المستخدم
        if isinstance(update, Update):
            if update.effective_user:
                user_id = update.effective_user.id
                error_context = f"user_{user_id}"
            elif update.callback_query and update.callback_query.from_user:
                user_id = update.callback_query.from_user.id
                error_context = f"callback_{user_id}"
            elif update.message and update.message.from_user:
                user_id = update.message.from_user.id
                error_context = f"message_{user_id}"
        
        # معالجة خاصة للأخطاء الشائعة
        error_str = str(context.error)
        
        # خطأ التعارض في getUpdates
        if "Conflict: terminated by other getUpdates request" in error_str:
            logger.warning("Detected multiple bot instances conflict. Bot will continue with retry logic.")
            return
        
        # أخطاء الشبكة (httpx.ReadError وما شابه)
        if any(error_type in error_str for error_type in [
            "httpx.ReadError", "ReadError", "ConnectionError", "TimeoutError", 
            "ReadTimeout", "ConnectTimeout", "PoolTimeout", "RemoteDisconnected"
        ]):
            logger.warning(f"Network error detected: {error_str}")
            # لا نرسل رسالة للمستخدم لأن هذه أخطاء شبكة مؤقتة
            if user_id:
                # فقط تنظيف البيانات المؤقتة بدون إرسال رسالة
                context.user_data.clear()
            return
            
        # تسجيل الخطأ
        error_msg = f"Global error in {error_context}: {context.error}"
        logger.error(error_msg, exc_info=context.error)
        
        # تنظيف البيانات المؤقتة للمستخدم إذا كان معروف
        if user_id:
            # تم إزالة health_monitor.mark_user_stuck
            
            # تنظيف البيانات المؤقتة للمستخدم
            context.user_data.clear()
            
            # محاولة إرسال رسالة للمستخدم
            try:
                if isinstance(update, Update) and update.effective_chat:
                    await context.bot.send_message(
                        update.effective_chat.id,
                        "⚠️ حدث خطأ غير متوقع. تم إعادة تعيين حالتك.\n"
                        "يرجى استخدام /start لإعادة تشغيل البوت.",
                        reply_markup=ReplyKeyboardRemove()
                    )
            except Exception as send_error:
                logger.error(f"Failed to send error message to user {user_id}: {send_error}")
        
        # إحصائيات الأخطاء
        error_type = type(context.error).__name__
        if not hasattr(global_error_handler, 'error_stats'):
            global_error_handler.error_stats = {}
        
        global_error_handler.error_stats[error_type] = global_error_handler.error_stats.get(error_type, 0) + 1
        
        # إذا كان هناك أكثر من 10 أخطاء من نفس النوع، أرسل تنبيه للأدمن
        if global_error_handler.error_stats[error_type] == 10:
            try:
                await context.bot.send_message(
                    ADMIN_CHAT_ID,
                    f"🚨 تحذير: تم تسجيل 10 أخطاء من نوع {error_type}\n"
                    f"آخر خطأ: {str(context.error)[:200]}..."
                )
            except:
                pass
                
    except Exception as handler_error:
        # إذا فشل معالج الأخطاء نفسه
        logger.critical(f"Error in global error handler: {handler_error}", exc_info=handler_error)

# نظام إدارة حالة الخدمات المتقدم
SERVICE_STATUS_DB = "service_status.db"

def init_service_status_db():
    """تهيئة قاعدة بيانات حالة الخدمات"""
    conn = sqlite3.connect(SERVICE_STATUS_DB)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS service_status (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            service_type TEXT NOT NULL,     -- 'static' أو 'socks'
            sub_type TEXT,                  -- 'weekly', 'monthly', 'residential', etc.
            country TEXT NOT NULL,          -- 'US', 'UK', etc.
            state TEXT,                     -- 'NY', 'CA', etc. (للولايات الأمريكية فقط)
            is_enabled BOOLEAN DEFAULT 1,  -- 1 = مفعل, 0 = معطل
            disabled_reason TEXT,           -- سبب التعطيل
            last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_by INTEGER              -- معرف الأدمن الذي قام بالتحديث
        )
    ''')
    
    # إنشاء فهرس للبحث السريع
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_service_lookup 
        ON service_status(service_type, sub_type, country, state)
    ''')
    
    conn.commit()
    conn.close()

def check_service_enabled(service_type, sub_type, country, state=None):
    """فحص ما إذا كانت الخدمة مفعلة أم لا"""
    conn = sqlite3.connect(SERVICE_STATUS_DB)
    cursor = conn.cursor()
    
    # البحث الدقيق أولاً (مع الولاية إن وجدت)
    if state:
        cursor.execute("""
            SELECT is_enabled, disabled_reason FROM service_status 
            WHERE service_type = ? AND sub_type = ? AND country = ? AND state = ?
        """, (service_type, sub_type, country, state))
        result = cursor.fetchone()
        if result:
            conn.close()
            return result[0] == 1, result[1]
    
    # البحث على مستوى الدولة فقط
    cursor.execute("""
        SELECT is_enabled, disabled_reason FROM service_status 
        WHERE service_type = ? AND sub_type = ? AND country = ? AND state IS NULL
    """, (service_type, sub_type, country))
    result = cursor.fetchone()
    if result:
        conn.close()
        return result[0] == 1, result[1]
    
    # البحث على مستوى النوع والدولة (بدون sub_type)
    cursor.execute("""
        SELECT is_enabled, disabled_reason FROM service_status 
        WHERE service_type = ? AND sub_type IS NULL AND country = ? AND state IS NULL
    """, (service_type, country))
    result = cursor.fetchone()
    if result:
        conn.close()
        return result[0] == 1, result[1]
    
    # البحث على مستوى النوع العام
    cursor.execute("""
        SELECT is_enabled, disabled_reason FROM service_status 
        WHERE service_type = ? AND sub_type IS NULL AND country IS NULL AND state IS NULL
    """, (service_type,))
    result = cursor.fetchone()
    if result:
        conn.close()
        return result[0] == 1, result[1]
    
    conn.close()
    # افتراضياً الخدمة مفعلة إذا لم توجد قاعدة
    return True, None

def set_service_status(service_type, sub_type, country, state, is_enabled, disabled_reason, admin_id):
    """تحديث حالة الخدمة"""
    conn = sqlite3.connect(SERVICE_STATUS_DB)
    cursor = conn.cursor()
    
    # فحص وجود القاعدة
    cursor.execute("""
        SELECT id FROM service_status 
        WHERE service_type = ? AND sub_type = ? AND country = ? AND 
              (state = ? OR (state IS NULL AND ? IS NULL))
    """, (service_type, sub_type, country, state, state))
    
    existing = cursor.fetchone()
    
    if existing:
        # تحديث القاعدة الموجودة
        cursor.execute("""
            UPDATE service_status 
            SET is_enabled = ?, disabled_reason = ?, last_updated = CURRENT_TIMESTAMP, updated_by = ?
            WHERE id = ?
        """, (is_enabled, disabled_reason, admin_id, existing[0]))
    else:
        # إنشاء قاعدة جديدة
        cursor.execute("""
            INSERT INTO service_status (service_type, sub_type, country, state, is_enabled, disabled_reason, updated_by)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (service_type, sub_type, country, state, is_enabled, disabled_reason, admin_id))
    
    conn.commit()
    conn.close()

async def handle_manage_external_proxy(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالجة إدارة بروكسي خارجي - مؤقتاً بدون وظيفة"""
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [
            InlineKeyboardButton("🔙 رجوع لإدارة البروكسيات", callback_data="back_to_manage_proxies")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    message = """🌐 **إدارة بروكسي خارجي**

⚠️ هذه الميزة قيد التطوير حالياً

🚧 **قريباً ستتمكن من:**
• إضافة خوادم بروكسي خارجية
• إدارة اتصالات مع مزودي خدمة خارجيين
• مراقبة حالة الخوادم الخارجية
• تكوين إعدادات الاتصال المتقدمة

💡 سيتم تفعيل هذه الميزة في التحديث القادم"""
    
    await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')

async def handle_detailed_static_management(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالجة إدارة تفصيلية للخدمات الثابتة"""
    query = update.callback_query
    await query.answer()
    
    service_type = query.data.replace("manage_detailed_static_", "")
    
    keyboard = [
        [
            InlineKeyboardButton("🔴 تعطيل الخدمة", callback_data=f"toggle_{service_type}_disable"),
            InlineKeyboardButton("🟢 تفعيل الخدمة", callback_data=f"toggle_{service_type}_enable")
        ],
        [
            InlineKeyboardButton("🔙 رجوع للإدارة المتقدمة", callback_data="advanced_service_management")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    message = f"""⚙️ **إدارة تفصيلية - {service_type}**

🎯 يمكنك تفعيل أو تعطيل هذه الخدمة المحددة

⚠️ **ملاحظة:** عند التعطيل، سيتم إشعار جميع المستخدمين تلقائياً

📊 **الحالة الحالية:** قيد التحديث..."""
    
    await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')

async def handle_manage_static_states(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالجة إدارة ولايات الخدمات الثابتة"""
    query = update.callback_query
    await query.answer()
    
    keyboard = []
    for state_code, state_name in US_STATES_STATIC_RESIDENTIAL['ar'].items():
        keyboard.append([
            InlineKeyboardButton(f"🏛️ {state_name}", callback_data=f"manage_state_{state_code}")
        ])
    
    keyboard.append([
        InlineKeyboardButton("🔙 رجوع لإدارة البروكسيات", callback_data="back_to_manage_proxies")
    ])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    message = """🏛️ **إدارة ولايات الخدمات الثابتة**

🎯 اختر الولاية المراد إدارتها:

💡 يمكنك تفعيل أو تعطيل خدمات محددة لكل ولاية"""
    
    await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')

# وظائف إدارة البروكسيات المجانية والمدفوعة

async def handle_manage_free_proxies(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالجة زر إدارة البروكسيات الشامل - يشمل المجانية والمدفوعة"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    
    # التحقق من أن المستخدم هو أدمن
    if not context.user_data.get('is_admin', False):
        await query.edit_message_text("❌ ليس لديك صلاحية للوصول لهذا القسم")
        return
    
    # الحصول على حالة الخدمات الحالية للعرض
    static_enabled = any(db.get_service_subtypes_status('static').values())
    socks_enabled = any(db.get_service_subtypes_status('socks').values())
    
    # تكوين الرموز بناءً على الحالة
    static_icon = "🟢" if static_enabled else "🔴"
    socks_icon = "🟢" if socks_enabled else "🔴"
    
    keyboard = [
        # قسم إدارة خدمات البروكسي المدفوعة
        [InlineKeyboardButton("⚙️ تشغيل / إيقاف الخدمات", callback_data="manage_services")],
        [InlineKeyboardButton(f"{static_icon} إدارة خدمات الستاتيك", callback_data="manage_static_services")],
        [InlineKeyboardButton(f"{socks_icon} إدارة خدمات السوكس", callback_data="manage_socks_services")],
        [InlineKeyboardButton("⚡ التحكم السريع", callback_data="quick_service_control")],
        
        # فاصل
        [InlineKeyboardButton("━━━━━━━━━━━━━━━━━━━━", callback_data="separator")],
        
        # قسم إدارة البروكسيات المجانية
        [InlineKeyboardButton("🎁 إدارة البروكسيات المجانية", callback_data="manage_free_proxies_menu")],
        # النظام المتقدم لإدارة الخدمات
        [InlineKeyboardButton("⚙️ إدارة الخدمات المتقدمة", callback_data="advanced_service_management")],
        [InlineKeyboardButton("🌐 إدارة بروكسي خارجي", callback_data="manage_external_proxy")],
        [InlineKeyboardButton("➕ إضافة ستاتيك مجاني", callback_data="add_free_proxy")],
        [InlineKeyboardButton("🗑 حذف بروكسي مجاني", callback_data="delete_free_proxy")],
        
        # العودة
        [InlineKeyboardButton("🔙 رجوع", callback_data="back_to_admin_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "🌐 إدارة البروكسيات الشاملة\n\n"
        "🟢 = مفعل | 🔴 = معطل\n\n"
        "يمكنك إدارة جميع أنواع البروكسيات من هنا:\n"
        "• الخدمات المدفوعة (ستاتيك/سوكس)\n"
        "• البروكسيات المجانية\n"
        "• التحكم في الدول والولايات\n\n"
        "اختر الإجراء المطلوب:",
        reply_markup=reply_markup
    )

async def handle_free_proxy_trial(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالجة طلب تجربة البروكسي المجاني"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    language = get_user_language(user_id)
    
    # جلب جميع البروكسيات المجانية المتاحة
    proxies = db.execute_query("SELECT id, message FROM free_proxies ORDER BY id")
    
    if not proxies:
        if language == 'ar':
            message = "😔 عذراً، لا توجد بروكسيات تجريبية متاحة حالياً\n\nيرجى المحاولة لاحقاً أو التواصل مع الأدمن"
        else:
            message = "😔 Sorry, no trial proxies are currently available\n\nPlease try again later or contact admin"
        
        await query.edit_message_text(message)
        return
    
    # إنشاء أزرار البروكسيات المتاحة
    keyboard = []
    for proxy_id, message in proxies:
        if language == 'ar':
            button_text = f"بروكسي #{proxy_id}"
        else:
            button_text = f"Proxy #{proxy_id}"
        
        keyboard.append([InlineKeyboardButton(button_text, callback_data=f"use_free_proxy_{proxy_id}")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if language == 'ar':
        message_text = "🎁 البروكسيات التجريبية المتاحة:\n\nاختر البروكسي الذي تريد تجربته:"
    else:
        message_text = "🎁 Available trial proxies:\n\nChoose the proxy you want to try:"
    
    await query.edit_message_text(message_text, reply_markup=reply_markup)

async def handle_use_free_proxy(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """إرسال البروكسي المجاني للمستخدم"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    language = get_user_language(user_id)
    proxy_id = int(query.data.split("_")[3])
    
    # جلب بيانات البروكسي
    result = db.execute_query("SELECT message FROM free_proxies WHERE id = ?", (proxy_id,))
    
    if not result:
        if language == 'ar':
            error_msg = "❌ البروكسي غير متاح حالياً"
        else:
            error_msg = "❌ Proxy is not available currently"
        
        await query.edit_message_text(error_msg)
        return
    
    proxy_message = result[0][0]
    
    if language == 'ar':
        final_message = f"🎁 بروكسي مجاني #{proxy_id}\n\n{proxy_message}\n\n⏰ يرجى ملاحظة أن البروكسيات المجانية قد تكون أبطأ من المدفوعة"
    else:
        final_message = f"🎁 Free Proxy #{proxy_id}\n\n{proxy_message}\n\n⏰ Please note that free proxies may be slower than paid ones"
    
    await query.edit_message_text(final_message)

async def handle_manage_proxies(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالجة زر إدارة البروكسيات"""
    user_id = update.effective_user.id
    
    # التحقق من أن المستخدم هو أدمن
    if not context.user_data.get('is_admin', False):
        await update.message.reply_text("❌ ليس لديك صلاحية للوصول لهذا القسم")
        return
    
    keyboard = [
        [InlineKeyboardButton("⚙️ تشغيل / إيقاف الخدمات", callback_data="manage_services")],
        [InlineKeyboardButton("🎁 إدارة البروكسيات المجانية", callback_data="manage_free_proxies_menu")],
        [InlineKeyboardButton("🌍 إدارة البروكسيات الخارجية", callback_data="manage_external_proxies")],
        [InlineKeyboardButton("❌ رجوع", callback_data="back_to_admin_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🌐 إدارة البروكسيات\n\nاختر الإجراء المطلوب:",
        reply_markup=reply_markup
    )

async def handle_manage_free_proxies_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالجة قائمة إدارة البروكسيات المجانية الفرعية"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    
    # التحقق من أن المستخدم هو أدمن
    if not context.user_data.get('is_admin', False):
        await query.edit_message_text("❌ ليس لديك صلاحية للوصول لهذا القسم")
        return
    
    keyboard = [
        [InlineKeyboardButton("➕ إضافة ستاتيك مجاني", callback_data="add_free_proxy")],
        [InlineKeyboardButton("🗑 حذف بروكسي مجاني", callback_data="delete_free_proxy")],
        [InlineKeyboardButton("🔙 رجوع لإدارة البروكسيات", callback_data="back_to_manage_proxies")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "🎁 إدارة البروكسيات المجانية\n\nاختر الإجراء المطلوب:",
        reply_markup=reply_markup
    )

async def handle_manage_external_proxies(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالجة إدارة البروكسيات الخارجية"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    
    # التحقق من أن المستخدم هو أدمن
    if not context.user_data.get('is_admin', False):
        await query.edit_message_text("❌ ليس لديك صلاحية للوصول لهذا القسم")
        return
    
    keyboard = [
        [InlineKeyboardButton("🔙 رجوع لإدارة البروكسيات", callback_data="back_to_manage_proxies")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "🌍 إدارة البروكسيات الخارجية\n\n🚧 هذه الميزة قيد التطوير حالياً\n\nسيتم إضافة المزيد من الخيارات قريباً...",
        reply_markup=reply_markup
    )

async def handle_add_free_proxy(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """بدء إضافة بروكسي مجاني"""
    query = update.callback_query
    await query.answer()
    
    keyboard = [[InlineKeyboardButton("🔙 رجوع العملية", callback_data="cancel_add_proxy")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "📝 أرسل الآن رسالة البروكسي المجاني التي تريد حفظها:\n\n"
        "مثال:\n"
        "```\n"
        "🎁 بروكسي تجريبي مجاني\n"
        "IP: 192.168.1.1\n"
        "Port: 8080\n"
        "```",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    
    return ADD_FREE_PROXY

async def handle_free_proxy_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """معالجة رسالة البروكسي المجاني"""
    message_content = update.message.text
    
    # حفظ الرسالة في قاعدة البيانات
    try:
        db.execute_query(
            "INSERT INTO free_proxies (message) VALUES (?)",
            (message_content,)
        )
        
        # الحصول على أعلى رقم ID لترقيم البروكسي
        result = db.execute_query("SELECT MAX(id) FROM free_proxies")
        proxy_id = result[0][0] if result and result[0][0] else 1
        
        await update.message.reply_text(
            f"✅ تم حفظ البروكسي بنجاح!\n\n"
            f"🆔 رقم البروكسي: #{proxy_id}\n"
            f"📅 التاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
            f"💡 البروكسي أصبح متوفراً كعينة للزبائن"
        )
        
        # العودة للقائمة الرئيسية
        await restore_admin_keyboard(context, update.effective_user.id, "🔧 تم إضافة البروكسي بنجاح")
        
    except Exception as e:
        logger.error(f"Error saving free proxy: {e}")
        await update.message.reply_text("❌ حدث خطأ في حفظ البروكسي. يرجى المحاولة مرة أخرى.")
    
    return ConversationHandler.END

async def handle_delete_free_proxy(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """عرض قائمة البروكسيات المحفوظة للحذف"""
    query = update.callback_query
    await query.answer()
    
    # جلب جميع البروكسيات المحفوظة
    proxies = db.execute_query("SELECT id, message FROM free_proxies ORDER BY id")
    
    if not proxies:
        await query.edit_message_text(
            "📭 لا توجد بروكسيات محفوظة حالياً",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ رجوع", callback_data="back_to_manage_proxies")]])
        )
        return ConversationHandler.END
    
    # إنشاء أزرار البروكسيات
    keyboard = []
    for proxy_id, message in proxies:
        # عرض أول 30 حرف من الرسالة كعنوان
        title = message[:30] + "..." if len(message) > 30 else message
        keyboard.append([InlineKeyboardButton(f"بروكسي #{proxy_id}: {title}", callback_data=f"view_proxy_{proxy_id}")])
    
    keyboard.append([InlineKeyboardButton("❌ رجوع", callback_data="back_to_manage_proxies")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "🗑 اختر البروكسي المراد حذفه:",
        reply_markup=reply_markup
    )
    
    return DELETE_FREE_PROXY

async def handle_view_proxy_for_delete(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """عرض البروكسي مع خيارات الحذف أو التراجع"""
    query = update.callback_query
    await query.answer()
    
    proxy_id = int(query.data.split("_")[2])
    
    # جلب بيانات البروكسي
    result = db.execute_query("SELECT message, created_at FROM free_proxies WHERE id = ?", (proxy_id,))
    
    if not result:
        await query.edit_message_text("❌ البروكسي غير موجود")
        return ConversationHandler.END
    
    message, created_at = result[0]
    
    keyboard = [
        [InlineKeyboardButton("🗑 حذف", callback_data=f"confirm_delete_{proxy_id}")],
        [InlineKeyboardButton("❌ تراجع", callback_data="delete_free_proxy")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"📋 بروكسي #{proxy_id}\n"
        f"📅 تاريخ الإنشاء: {created_at}\n\n"
        f"📝 المحتوى:\n{message}",
        reply_markup=reply_markup
    )
    
    return DELETE_FREE_PROXY

async def handle_confirm_delete_proxy(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """تأكيد حذف البروكسي"""
    query = update.callback_query
    await query.answer()
    
    proxy_id = int(query.data.split("_")[2])
    
    try:
        # حذف البروكسي من قاعدة البيانات
        db.execute_query("DELETE FROM free_proxies WHERE id = ?", (proxy_id,))
        
        await query.edit_message_text(f"✅ تم حذف بروكسي #{proxy_id} بنجاح")
        
        # العودة للقائمة الرئيسية
        await restore_admin_keyboard(context, update.effective_user.id, "🗑 تم حذف البروكسي بنجاح")
        
    except Exception as e:
        logger.error(f"Error deleting proxy {proxy_id}: {e}")
        await query.edit_message_text("❌ حدث خطأ في حذف البروكسي")
    
    return ConversationHandler.END

async def handle_cancel_add_proxy(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """إلغاء إضافة البروكسي"""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text("❌ تم إلغاء عملية إضافة البروكسي")
    await restore_admin_keyboard(context, update.effective_user.id, "🔧 تم إلغاء العملية")
    
    return ConversationHandler.END

async def handle_back_to_manage_proxies(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """العودة لقائمة إدارة البروكسيات"""
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("⚙️ تشغيل / إيقاف الخدمات", callback_data="manage_services")],
        [InlineKeyboardButton("🎁 إدارة البروكسيات المجانية", callback_data="manage_free_proxies_menu")],
        [InlineKeyboardButton("🌍 إدارة البروكسيات الخارجية", callback_data="manage_external_proxies")],
        [InlineKeyboardButton("❌ رجوع", callback_data="back_to_admin_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "🌐 إدارة البروكسيات\n\nاختر الإجراء المطلوب:",
        reply_markup=reply_markup
    )

async def handle_back_to_admin_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """العودة للقائمة الرئيسية للأدمن"""
    query = update.callback_query
    await query.answer()
    
    await query.delete_message()
    await restore_admin_keyboard(context, update.effective_user.id, "🔧 لوحة الأدمن جاهزة")

# وظائف المستخدمين للبروكسيات المجانية

async def handle_free_static_trial(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالجة طلب تجربة ستاتيك مجانا"""
    user_id = update.effective_user.id
    language = get_user_language(user_id)
    
    # جلب جميع البروكسيات المجانية المتاحة
    proxies = db.execute_query("SELECT id, message FROM free_proxies ORDER BY id")
    
    if not proxies:
        if language == 'ar':
            message = "😔 عذراً، لا توجد بروكسيات تجريبية متاحة حالياً\n\nيرجى المحاولة لاحقاً أو التواصل مع الأدمن"
        else:
            message = "😔 Sorry, no trial proxies are currently available\n\nPlease try again later or contact admin"
        
        await update.message.reply_text(message)
        return
    
    # إنشاء أزرار البروكسيات المتاحة
    keyboard = []
    for proxy_id, message in proxies:
        if language == 'ar':
            button_text = f"بروكسي #{proxy_id}"
        else:
            button_text = f"Proxy #{proxy_id}"
        
        keyboard.append([InlineKeyboardButton(button_text, callback_data=f"use_free_proxy_{proxy_id}")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if language == 'ar':
        message_text = "🎁 البروكسيات التجريبية المتاحة:\n\nاختر البروكسي الذي تريد تجربته:"
    else:
        message_text = "🎁 Available trial proxies:\n\nChoose the proxy you want to try:"
    
    await update.message.reply_text(message_text, reply_markup=reply_markup)

async def handle_get_free_proxy(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """إرسال البروكسي المجاني للمستخدم"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    language = get_user_language(user_id)
    proxy_id = int(query.data.split("_")[3])
    
    # جلب بيانات البروكسي
    result = db.execute_query("SELECT message FROM free_proxies WHERE id = ?", (proxy_id,))
    
    if not result:
        if language == 'ar':
            error_msg = "❌ البروكسي غير متاح حالياً"
        else:
            error_msg = "❌ Proxy is not available currently"
        
        await query.edit_message_text(error_msg)
        return
    
    proxy_message = result[0][0]
    
    if language == 'ar':
        thank_message = f"🎁 هذه عينة مجانية، استمتع بوقتك!\n\n{proxy_message}"
    else:
        thank_message = f"🎁 This is a free sample, enjoy your time!\n\n{proxy_message}"
    
    await query.edit_message_text(thank_message)
    
    # تسجيل العملية في اللوجس
    db.log_action(user_id, f"free_proxy_used_{proxy_id}")

# دوال التحقق من حالة الخدمات والإشعارات

async def check_service_availability(service_type: str, update: Update, context: ContextTypes.DEFAULT_TYPE, language: str) -> bool:
    """التحقق من توفر خدمة معينة"""
    # للستاتيك، نحتاج للتحقق من حالة الخدمة الأساسية
    if service_type == 'static':
        if not db.get_service_status('static', 'basic'):
            await send_service_disabled_message(update, language, 'static', 'الستاتيك الأساسية')
            return False
    elif service_type == 'socks':
        if not db.get_service_status('socks', 'basic'):
            await send_service_disabled_message(update, language, 'socks', 'السوكس الأساسية')
            return False
    
    return True

async def send_service_disabled_message(update: Update, language: str, service_type: str, service_name: str):
    """إرسال رسالة تعطيل الخدمة للمستخدم"""
    if language == 'ar':
        message = f"""🚫 تم إيقاف خدمة {service_name}
        
⚠️ عذراً، تم إيقاف هذه الخدمة مؤقتاً من قبل الإدارة

🔸 الأسباب المحتملة:
• نفاد الكمية المتاحة
• تعطل مؤقت في سيرفرات الخدمة
• صيانة فنية

🔔 سيتم إعلامكم فور إعادة تشغيل الخدمة

💫 شكراً لتفهمكم وصبركم"""
    else:
        message = f"""🚫 {service_name} Service Disabled
        
⚠️ Sorry, this service is temporarily disabled by administration

🔸 Possible reasons:
• Available quantity exhausted
• Temporary server issues
• Technical maintenance

🔔 You will be notified once the service is restored

💫 Thank you for your understanding and patience"""
    
    try:
        if hasattr(update, 'callback_query') and update.callback_query:
            await update.callback_query.edit_message_text(message)
        else:
            await update.message.reply_text(message)
    except Exception as e:
        print(f"خطأ في إرسال رسالة تعطيل الخدمة: {e}")

async def broadcast_service_notification(service_name: str, is_enabled: bool, service_type: str = None):
    """إرسال إشعار لجميع المستخدمين عند تغيير حالة الخدمة"""
    try:
        # ترجمة الأسماء من العربية إلى الإنجليزية
        service_translations = {
            'بروكسي داتا سينتر': 'Datacenter Proxy',
            'ريزيدنتال': 'Residential',
            'ريزيدنتال Verizon': 'Verizon Residential',
            'ريزيدنتال Crocker': 'Crocker Residential',
            'ISP': 'ISP',
            'جميع خدمات الستاتيك': 'All Static Services',
            'جميع خدمات السوكس': 'All SOCKS Services',
            'خدمات السوكس الأساسية': 'Basic SOCKS Services',
            'الستاتيك الأساسية': 'Basic Static',
            'السوكس الأساسية': 'Basic SOCKS',
            'جميع دول السوكس': 'All SOCKS Countries',
            'جميع ولايات أمريكا للستاتيك': 'All US States for Static',
            'السوكس الأمريكية': 'American SOCKS',
            'السوكس الإسبانية': 'Spanish SOCKS',
            'السوكس البريطانية': 'British SOCKS',
            'السوكس الكندية': 'Canadian SOCKS',
            'السوكس الألمانية': 'German SOCKS',
            'السوكس الإيطالية': 'Italian SOCKS',
            'السوكس السويدية': 'Swedish SOCKS'
        }
        
        # استخدام الترجمة إن وُجدت، وإلا استخدام الاسم كما هو
        service_name_en = service_translations.get(service_name, service_name)
        
        # الحصول على جميع المستخدمين
        users = db.execute_query("SELECT user_id FROM users WHERE is_banned = 0")
        
        if is_enabled:
            # رسالة تشغيل الخدمة
            ar_message = f"""✅ تم إعادة تشغيل خدمة {service_name}
            
🎉 خبر سار! تم إعادة تفعيل الخدمة

🔸 الخدمة متاحة الآن للطلب
🚀 يمكنكم البدء بإنشاء طلباتكم
⭐ جودة عالية وسرعة ممتازة

💫 شكراً لصبركم وثقتكم بنا"""
            
            en_message = f"""✅ {service_name_en} Service Restored
            
🎉 Great news! The service has been reactivated

🔸 Service is now available for orders
🚀 You can start creating your orders
⭐ High quality and excellent speed

💫 Thank you for your patience and trust"""
        else:
            # رسالة إيقاف الخدمة
            ar_message = f"""🚫 تم إيقاف خدمة {service_name}
            
⚠️ تم إيقاف هذه الخدمة مؤقتاً من قبل الإدارة

🔸 الأسباب المحتملة:
• نفاد الكمية المتاحة
• تعطل مؤقت في سيرفرات الخدمة
• صيانة فنية

🔔 سيتم إعلامكم فور إعادة تشغيل الخدمة

💫 شكراً لتفهمكم وصبركم"""
            
            en_message = f"""🚫 {service_name_en} Service Disabled
            
⚠️ This service has been temporarily disabled by administration

🔸 Possible reasons:
• Available quantity exhausted
• Temporary server issues
• Technical maintenance

🔔 You will be notified once service is restored

💫 Thank you for your understanding and patience"""
        
        # إرسال الإشعارات
        success_count = 0
        for user_row in users:
            try:
                user_id = user_row[0]
                language = get_user_language(user_id)
                message = ar_message if language == 'ar' else en_message
                
                from telegram import Bot
                bot = Bot(token=TOKEN)
                await bot.send_message(
                    chat_id=user_id,
                    text=message,
                    parse_mode='HTML'
                )
                success_count += 1
                
                # تأخير صغير لتجنب حدود الإرسال
                await asyncio.sleep(0.05)
                
            except Exception as user_error:
                print(f"فشل إرسال إشعار للمستخدم {user_id}: {user_error}")
                continue
        
        print(f"✅ تم إرسال إشعار تغيير حالة الخدمة {service_name} إلى {success_count} مستخدم")
        
    except Exception as e:
        print(f"خطأ في إرسال إشعارات تغيير حالة الخدمة: {e}")

# دوال إدارة خدمات البروكسي (تشغيل/إيقاف)

async def handle_manage_services(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالجة قائمة إدارة خدمات البروكسي"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    
    # التحقق من أن المستخدم هو أدمن
    if not context.user_data.get('is_admin', False):
        await query.edit_message_text("❌ ليس لديك صلاحية للوصول لهذا القسم")
        return
    
    keyboard = [
        [InlineKeyboardButton("🏠 إدارة خدمات الستاتيك", callback_data="manage_static_services")],
        [InlineKeyboardButton("🌐 إدارة خدمات السوكس", callback_data="manage_socks_services")],
        [InlineKeyboardButton("⚡ التحكم السريع", callback_data="quick_service_control")],
        [InlineKeyboardButton("🔙 رجوع", callback_data="back_to_manage_proxies")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "⚙️ إدارة خدمات البروكسي\n\n"
        "اختر نوع الخدمة التي تريد إدارتها:",
        reply_markup=reply_markup
    )

async def handle_manage_static_services(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالجة قائمة إدارة خدمات الستاتيك المحسّنة"""
    query = update.callback_query
    await query.answer()
    
    # الحصول على حالة جميع خدمات الستاتيك
    static_subtypes = db.get_service_subtypes_status('static')
    
    keyboard = []
    
    # إضافة زر تشغيل/إيقاف جميع خدمات الستاتيك
    all_enabled = all(static_subtypes.values()) if static_subtypes else True
    toggle_all_text = "❌ إيقاف جميع خدمات الستاتيك" if all_enabled else "✅ تشغيل جميع خدمات الستاتيك"
    keyboard.append([InlineKeyboardButton(toggle_all_text, callback_data=f"toggle_all_static_{not all_enabled}")])
    
    # إضافة فاصل
    keyboard.append([InlineKeyboardButton("━━━━━ خدمات الستاتيك الشهرية ━━━━━", callback_data="separator")])
    
    # أزرار الخدمات الشهرية
    monthly_services = {
        'monthly_residential': {'name': '🏢 ريزيدنتال', 'price': '6$', 'desc': 'عالي الجودة'},
        'monthly_verizon': {'name': '🏠 ريزيدنتال Crocker', 'price': '4$', 'desc': 'جودة ممتازة'}, 
    }
    
    for service_type, info in monthly_services.items():
        is_enabled = static_subtypes.get(service_type, True)
        status = "🟢" if is_enabled else "🔴"
        action = "disable" if is_enabled else "enable"
        availability = f"متاح" if is_enabled else "معطل"
        
        keyboard.append([InlineKeyboardButton(
            f"{status} {info['name']} ({info['price']}) - {availability}", 
            callback_data=f"toggle_static_{service_type}_{action}"
        )])
        # إضافة زر إدارة تفصيلية لكل خدمة
        keyboard.append([InlineKeyboardButton(
            f"⚙️ إدارة {info['name']} بالتفصيل", 
            callback_data=f"manage_detailed_static_{service_type}"
        )])
    
    # إضافة فاصل للخدمات الأسبوعية/اليومية
    keyboard.append([InlineKeyboardButton("━━━━━ خدمات الستاتيك المؤقتة ━━━━━", callback_data="separator")])
    
    # أزرار الخدمات المؤقتة
    temp_services = {
        'weekly_crocker': {'name': '📅 ستاتيك أسبوعي Crocker', 'price': '2.5$', 'desc': 'أسبوعي'},
        'daily_static': {'name': '📅 ستاتيك يومي', 'price': '0$', 'desc': 'مجاني يومي'}
    }
    
    for service_type, info in temp_services.items():
        is_enabled = static_subtypes.get(service_type, True)
        status = "🟢" if is_enabled else "🔴"
        action = "disable" if is_enabled else "enable"
        availability = f"متاح" if is_enabled else "معطل"
        
        keyboard.append([InlineKeyboardButton(
            f"{status} {info['name']} ({info['price']}) - {availability}", 
            callback_data=f"toggle_static_{service_type}_{action}"
        )])
    
    # إضافة فاصل للخدمات المتخصصة
    keyboard.append([InlineKeyboardButton("━━━━━ خدمات متخصصة ━━━━━", callback_data="separator")])
    
    # الخدمات المتخصصة
    specialized_services = {
        'isp_att': {'name': '🌐 ISP', 'price': '3$', 'desc': 'ISP عشوائي'},
        'datacenter': {'name': '🔧 بروكسي داتا سينتر', 'price': '12$', 'desc': 'عالي السرعة'}
    }
    
    for service_type, info in specialized_services.items():
        is_enabled = static_subtypes.get(service_type, True)
        status = "🟢" if is_enabled else "🔴"
        action = "disable" if is_enabled else "enable"
        availability = f"متاح" if is_enabled else "معطل"
        
        keyboard.append([InlineKeyboardButton(
            f"{status} {info['name']} ({info['price']}) - {availability}", 
            callback_data=f"toggle_static_{service_type}_{action}"
        )])
        # إدارة تفصيلية للخدمات المتخصصة
        keyboard.append([InlineKeyboardButton(
            f"⚙️ إدارة {info['name']} بالتفصيل", 
            callback_data=f"manage_detailed_static_{service_type}"
        )])
    
    # أزرار الإدارة العامة
    keyboard.append([InlineKeyboardButton("━━━━━━━━━━━━━━━━━━━━━━━", callback_data="separator")])
    keyboard.append([
        InlineKeyboardButton("🌍 إدارة الدول", callback_data="manage_static_countries"),
        InlineKeyboardButton("🏛️ إدارة الولايات", callback_data="manage_static_states")
    ])
    keyboard.append([InlineKeyboardButton("📊 تقارير الخدمات", callback_data="static_services_report")])
    
    keyboard.append([InlineKeyboardButton("🔙 رجوع", callback_data="manage_services")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "🏠 إدارة خدمات الستاتيك المحسّنة\n\n"
        "🟢 = مفعل | 🔴 = معطل\n"
        "━━━━━━━━━━━━━━━━━━━━━━━\n"
        "يمكنك التحكم في كل خدمة على حدة أو إدارتها بالتفصيل:",
        reply_markup=reply_markup
    )

async def handle_manage_socks_services(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالجة قائمة إدارة خدمات السوكس"""
    query = update.callback_query
    await query.answer()
    
    # الحصول على حالة جميع خدمات السوكس
    socks_subtypes = db.get_service_subtypes_status('socks')
    
    keyboard = []
    
    # إضافة زر تشغيل/إيقاف جميع خدمات السوكس
    all_enabled = all(socks_subtypes.values()) if socks_subtypes else True
    toggle_all_text = "❌ إيقاف جميع خدمات السوكس" if all_enabled else "✅ تشغيل جميع خدمات السوكس"
    keyboard.append([InlineKeyboardButton(toggle_all_text, callback_data=f"toggle_all_socks_{not all_enabled}")])
    
    # أزرار الخدمات الفردية
    service_names = {
        'single': '🔸 بروكسي واحد (0.15$)',
        'package_2': '🔸 بروكسيان اثنان (0.25$)', 
        'package_5': '📦 باكج 5 (0.4$)',
        'package_10': '📦 باكج 10 (0.7$)',
        'basic': '🌐 خدمات السوكس الأساسية'
    }
    
    for service_type, name in service_names.items():
        is_enabled = socks_subtypes.get(service_type, True)
        status = "🟢" if is_enabled else "🔴"
        action = "disable" if is_enabled else "enable"
        keyboard.append([InlineKeyboardButton(
            f"{status} {name}", 
            callback_data=f"toggle_socks_{service_type}_{action}"
        )])
    
    # أزرار إدارة الدول
    keyboard.append([InlineKeyboardButton("🌍 إدارة الدول", callback_data="manage_socks_countries")])
    
    keyboard.append([InlineKeyboardButton("🔙 رجوع", callback_data="manage_services")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "🌐 إدارة خدمات السوكس\n\n"
        "🟢 = مفعل | 🔴 = معطل\n"
        "اضغط على الخدمة لتغيير حالتها:",
        reply_markup=reply_markup
    )

async def handle_quick_service_control(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالجة التحكم السريع في المستوى الأعلى للخدمات"""
    query = update.callback_query
    await query.answer()
    
    # التحقق من أن المستخدم هو أدمن
    if not context.user_data.get('is_admin', False):
        await query.edit_message_text("❌ ليس لديك صلاحية للوصول لهذا القسم")
        return
    
    # الحصول على حالة الخدمات الرئيسية
    static_enabled = any(db.get_service_subtypes_status('static').values())
    socks_enabled = any(db.get_service_subtypes_status('socks').values())
    
    keyboard = []
    
    # أزرار التحكم في المستوى الأعلى
    static_status = "🟢" if static_enabled else "🔴"
    static_action = "disable" if static_enabled else "enable"
    keyboard.append([InlineKeyboardButton(
        f"{static_status} جميع خدمات الستاتيك", 
        callback_data=f"toggle_all_static_{not static_enabled}"
    )])
    
    socks_status = "🟢" if socks_enabled else "🔴"
    socks_action = "disable" if socks_enabled else "enable"
    keyboard.append([InlineKeyboardButton(
        f"{socks_status} جميع خدمات السوكس", 
        callback_data=f"toggle_all_socks_{not socks_enabled}"
    )])
    
    # أزرار تحكم سريعة إضافية
    keyboard.append([InlineKeyboardButton("🌍 إيقاف جميع الدول", callback_data="disable_all_countries")])
    keyboard.append([InlineKeyboardButton("🌍 تشغيل جميع الدول", callback_data="enable_all_countries")])
    
    # زر العودة
    keyboard.append([InlineKeyboardButton("🔙 رجوع", callback_data="manage_services")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "⚡ التحكم السريع في الخدمات\n\n"
        "🟢 = مفعل | 🔴 = معطل\n\n"
        "يمكنك تشغيل أو إيقاف جميع الخدمات بضغطة واحدة:",
        reply_markup=reply_markup
    )

async def handle_toggle_service(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالجة تشغيل/إيقاف خدمة معينة"""
    query = update.callback_query
    await query.answer()
    
    callback_data = query.data
    
    try:
        service_names = {
            'monthly_residential': 'الستاتيك الشهرية الريزيدنتال',
            'monthly_verizon': 'الستاتيك الشهرية Crocker', 
            'weekly_crocker': 'الستاتيك الأسبوعية Crocker',
            'daily_static': 'الستاتيك اليومية',
            'isp_att': 'ستاتيك ISP',
            'datacenter': 'بروكسي داتا سينتر',
            'basic': 'الأساسية',
            'single': 'السوكس الواحد',
            'package_2': 'السوكس اثنان',
            'package_5': 'السوكس باكج 5',
            'package_10': 'السوكس باكج 10'
        }
        
        if callback_data.startswith("toggle_all_static_"):
            # تشغيل/إيقاف جميع خدمات الستاتيك
            enable = callback_data.split("_")[-1] == "True"
            db.toggle_all_service_subtypes('static', enable)
            
            # إرسال إشعار لجميع المستخدمين
            action_text = "تشغيل" if enable else "إيقاف"
            await broadcast_service_notification(f"جميع خدمات الستاتيك", enable)
            
            await handle_manage_static_services(update, context)
            
        elif callback_data.startswith("toggle_all_socks_"):
            # تشغيل/إيقاف جميع خدمات السوكس
            enable = callback_data.split("_")[-1] == "True"
            db.toggle_all_service_subtypes('socks', enable)
            
            # إرسال إشعار لجميع المستخدمين
            await broadcast_service_notification(f"جميع خدمات السوكس", enable)
            
            await handle_manage_socks_services(update, context)
            
        elif callback_data.startswith("toggle_static_"):
            # تشغيل/إيقاف خدمة ستاتيك محددة
            parts = callback_data.split("_")
            service_subtype = "_".join(parts[2:-1])
            action = parts[-1]
            enable = action == "enable"
            
            db.set_service_status('static', enable, service_subtype)
            
            # إرسال إشعار لجميع المستخدمين
            service_name = service_names.get(service_subtype, f"الستاتيك {service_subtype}")
            await broadcast_service_notification(service_name, enable, 'static')
            
            await handle_manage_static_services(update, context)
            
        elif callback_data.startswith("toggle_socks_"):
            # تشغيل/إيقاف خدمة سوكس محددة
            parts = callback_data.split("_")
            service_subtype = "_".join(parts[2:-1])
            action = parts[-1]
            enable = action == "enable"
            
            db.set_service_status('socks', enable, service_subtype)
            
            # إرسال إشعار لجميع المستخدمين
            if service_subtype == 'basic':
                service_name = "خدمات السوكس الأساسية"
            else:
                service_name = f"السوكس {service_subtype}"
            await broadcast_service_notification(service_name, enable, 'socks')
            
            await handle_manage_socks_services(update, context)
            
        elif callback_data.startswith("toggle_all_countries_"):
            # تشغيل/إيقاف جميع الدول
            enable = callback_data.split("_")[-1] == "True"
            db.toggle_all_countries('socks', 'basic', enable)
            await broadcast_service_notification(f"جميع دول السوكس", enable)
            await handle_manage_countries(update, context)
            
        elif callback_data.startswith("toggle_country_socks_"):
            # تشغيل/إيقاف دولة محددة للسوكس
            parts = callback_data.split("_")
            country_code = parts[3]
            action = parts[4]
            enable = action == "enable"
            
            db.set_service_status('socks', enable, 'basic', country_code)
            
            country_names = {
                'US': 'السوكس الأمريكية', 'FR': 'السوكس الفرنسية', 
                'ES': 'السوكس الإسبانية', 'UK': 'السوكس البريطانية',
                'CA': 'السوكس الكندية', 'DE': 'السوكس الألمانية',
                'IT': 'السوكس الإيطالية', 'SE': 'السوكس السويدية'
            }
            service_name = country_names.get(country_code, f"السوكس {country_code}")
            await broadcast_service_notification(service_name, enable, 'socks')
            
            await handle_manage_countries(update, context)
            
        elif callback_data.startswith("toggle_all_static_countries_"):
            # تشغيل/إيقاف جميع دول الستاتيك
            enable = callback_data.split("_")[-1] == "True"
            db.toggle_all_countries('static', 'monthly_residential', enable)
            await broadcast_service_notification(f"جميع دول الستاتيك", enable)
            await handle_manage_static_countries(update, context)
            
        elif callback_data.startswith("toggle_country_static_"):
            # تشغيل/إيقاف دولة محددة للستاتيك
            parts = callback_data.split("_")
            country_code = parts[3]
            action = parts[4]
            enable = action == "enable"
            
            db.set_service_status('static', enable, 'monthly_residential', country_code)
            
            country_names = {
                'US': '🇺🇸 الولايات المتحدة', 'UK': '🇬🇧 بريطانيا',
                'FR': '🇫🇷 فرنسا', 'DE': '🇩🇪 ألمانيا', 'AT': '🇦🇹 النمسا'
            }
            service_name = country_names.get(country_code, f"الستاتيك {country_code}")
            await broadcast_service_notification(service_name, enable, 'static')
            
            await handle_manage_static_countries(update, context)
            
        elif callback_data.startswith("toggle_all_us_states_"):
            # تشغيل/إيقاف جميع ولايات أمريكا للسوكس
            enable = callback_data.split("_")[-1] == "True"
            db.toggle_all_states('socks', 'US', 'basic', enable)
            await broadcast_service_notification(f"جميع ولايات أمريكا للسوكس", enable)
            await handle_manage_us_states(update, context)
            
        elif callback_data.startswith("toggle_state_socks_"):
            # تشغيل/إيقاف ولاية محددة للسوكس
            parts = callback_data.split("_")
            country_code = parts[3]  # US
            state_code = parts[4]
            action = parts[5]
            enable = action == "enable"
            
            db.set_service_status('socks', enable, 'basic', country_code, state_code)
            
            state_names = {
                'NY': '🏙️ نيويورك', 'CA': '🌴 كاليفورنيا', 'TX': '🤠 تكساس',
                'FL': '🏖️ فلوريدا', 'IL': '🏙️ إلينوي', 'PA': '🏛️ بنسلفانيا',
                'OH': '🌽 أوهايو', 'MI': '🚗 ميشيغان'
            }
            service_name = state_names.get(state_code, f"السوكس {state_code}")
            await broadcast_service_notification(service_name, enable, 'socks')
            
            await handle_manage_us_states(update, context)
            
        elif callback_data.startswith("toggle_all_static_us_states_"):
            # تشغيل/إيقاف جميع ولايات أمريكا للستاتيك
            enable = callback_data.split("_")[-1] == "True"
            db.toggle_all_states('static', 'US', 'monthly_residential', enable)
            db.toggle_all_states('static', 'US', 'monthly_verizon', enable)
            await broadcast_service_notification(f"جميع ولايات أمريكا للستاتيك", enable)
            await handle_manage_static_us_states(update, context)
            
        elif callback_data.startswith("toggle_state_static_"):
            # تشغيل/إيقاف ولاية محددة للستاتيك
            parts = callback_data.split("_")
            service_subtype = parts[3]  # residential أو verizon
            country_code = parts[4]  # US
            state_code = parts[5]
            action = parts[6]
            enable = action == "enable"
            
            # تحديد نوع الخدمة حسب النوع الفرعي
            if service_subtype == "residential":
                subtype = "monthly_residential"
            elif service_subtype == "verizon":
                subtype = "monthly_verizon"
            else:
                subtype = "monthly_residential"  # افتراضي
            
            db.set_service_status('static', enable, subtype, country_code, state_code)
            
            state_names = {
                'NY': '🏙️ نيويورك', 'CA': '🌴 كاليفورنيا', 'TX': '🤠 تكساس',
                'FL': '🏖️ فلوريدا', 'IL': '🏙️ إلينوي', 'PA': '🏛️ بنسلفانيا',
                'OH': '🌽 أوهايو', 'MI': '🚗 ميشيغان', 'GA': '🍑 جورجيا',
                'NC': '🏔️ شمال كارولينا', 'NJ': '🏙️ نيوجيرسي', 'VA': '🏛️ فيرجينيا'
            }
            service_name = state_names.get(state_code, f"الستاتيك {state_code}")
            await broadcast_service_notification(f"{service_name} ({service_subtype})", enable, 'static')
            
            await handle_manage_static_us_states(update, context)
            
        elif callback_data == "disable_all_countries":
            # إيقاف جميع الدول
            db.toggle_all_countries('static', 'monthly_residential', False)
            db.toggle_all_countries('socks', 'basic', False)
            await broadcast_service_notification("جميع الدول", False)
            await handle_quick_service_control(update, context)
            
        elif callback_data == "enable_all_countries":
            # تشغيل جميع الدول
            db.toggle_all_countries('static', 'monthly_residential', True)
            db.toggle_all_countries('socks', 'basic', True)
            await broadcast_service_notification("جميع الدول", True)
            await handle_quick_service_control(update, context)
            
        else:
            await query.edit_message_text("❌ إجراء غير صحيح")
            
    except Exception as e:
        print(f"خطأ في تشغيل/إيقاف الخدمة: {e}")
        await query.edit_message_text("❌ حدث خطأ أثناء تحديث الخدمة")

async def handle_manage_static_countries(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالجة إدارة دول الستاتيك"""
    query = update.callback_query
    await query.answer()
    
    countries = db.get_countries_status('static', 'monthly_residential')
    
    keyboard = []
    
    # زر تشغيل/إيقاف جميع الدول
    all_enabled = all(countries.values()) if countries else True
    toggle_all_text = "❌ إيقاف جميع دول الستاتيك" if all_enabled else "✅ تشغيل جميع دول الستاتيك"
    keyboard.append([InlineKeyboardButton(toggle_all_text, callback_data=f"toggle_all_static_countries_{not all_enabled}")])
    
    # أسماء الدول للستاتيك
    country_names = {
        'US': '🇺🇸 الولايات المتحدة',
        'UK': '🇬🇧 بريطانيا',
        'FR': '🇫🇷 فرنسا', 
        'DE': '🇩🇪 ألمانيا',
        'AT': '🇦🇹 النمسا'
    }
    
    # إنشاء صفوف من دولتين
    row = []
    for country_code, name in country_names.items():
        is_enabled = countries.get(country_code, True)
        status = "🟢" if is_enabled else "🔴"
        action = "disable" if is_enabled else "enable"
        
        button = InlineKeyboardButton(
            f"{status} {name}", 
            callback_data=f"toggle_country_static_{country_code}_{action}"
        )
        
        row.append(button)
        if len(row) == 2:
            keyboard.append(row)
            row = []
    
    # إضافة أي أزرار متبقية
    if row:
        keyboard.append(row)
    
    # زر أمريكا للولايات
    keyboard.append([InlineKeyboardButton("🇺🇸 إدارة ولايات أمريكا الستاتيك", callback_data="manage_static_us_states")])
    keyboard.append([InlineKeyboardButton("🔙 رجوع", callback_data="manage_static_services")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "🌍 إدارة دول الستاتيك\n\n"
        "🟢 = مفعل | 🔴 = معطل\n"
        "اضغط على الدولة لتغيير حالتها:",
        reply_markup=reply_markup
    )

async def handle_manage_countries(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالجة إدارة دول السوكس"""
    query = update.callback_query
    await query.answer()
    
    countries = db.get_countries_status('socks', 'basic')
    
    keyboard = []
    
    # زر تشغيل/إيقاف جميع الدول
    all_enabled = all(countries.values()) if countries else True
    toggle_all_text = "❌ إيقاف جميع الدول" if all_enabled else "✅ تشغيل جميع الدول"
    keyboard.append([InlineKeyboardButton(toggle_all_text, callback_data=f"toggle_all_countries_{not all_enabled}")])
    
    # أسماء الدول
    country_names = {
        'US': '🇺🇸 أمريكا',
        'FR': '🇫🇷 فرنسا', 
        'ES': '🇪🇸 إسبانيا',
        'UK': '🇬🇧 بريطانيا',
        'CA': '🇨🇦 كندا',
        'DE': '🇩🇪 ألمانيا',
        'IT': '🇮🇹 إيطاليا',
        'SE': '🇸🇪 السويد'
    }
    
    # إنشاء صفوف من دولتين
    row = []
    for country_code, name in country_names.items():
        is_enabled = countries.get(country_code, True)
        status = "🟢" if is_enabled else "🔴"
        action = "disable" if is_enabled else "enable"
        
        button = InlineKeyboardButton(
            f"{status} {name}", 
            callback_data=f"toggle_country_socks_{country_code}_{action}"
        )
        
        row.append(button)
        if len(row) == 2:
            keyboard.append(row)
            row = []
    
    # إضافة أي أزرار متبقية
    if row:
        keyboard.append(row)
    
    # زر أمريكا للولايات
    keyboard.append([InlineKeyboardButton("🇺🇸 إدارة ولايات أمريكا", callback_data="manage_us_states")])
    keyboard.append([InlineKeyboardButton("🔙 رجوع", callback_data="manage_socks_services")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "🌍 إدارة دول السوكس\n\n"
        "🟢 = مفعل | 🔴 = معطل\n"
        "اضغط على الدولة لتغيير حالتها:",
        reply_markup=reply_markup
    )

async def handle_manage_us_states(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالجة إدارة ولايات أمريكا للسوكس"""
    query = update.callback_query
    await query.answer()
    
    states = db.get_states_status('socks', 'basic', 'US')
    
    keyboard = []
    
    # زر تشغيل/إيقاف جميع الولايات
    all_enabled = all(states.values()) if states else True
    toggle_all_text = "❌ إيقاف جميع ولايات أمريكا" if all_enabled else "✅ تشغيل جميع ولايات أمريكا"
    keyboard.append([InlineKeyboardButton(toggle_all_text, callback_data=f"toggle_all_us_states_{not all_enabled}")])
    
    # أهم الولايات الأمريكية للسوكس
    state_names = {
        'NY': '🏙️ نيويورك',
        'CA': '🌴 كاليفورنيا', 
        'TX': '🤠 تكساس',
        'FL': '🏖️ فلوريدا',
        'IL': '🏢 إلينوي',
        'PA': '🏛️ بنسلفانيا',
        'OH': '🌽 أوهايو',
        'GA': '🍑 جورجيا',
        'NC': '🏔️ كارولينا الشمالية',
        'MI': '🚗 ميشيغان',
        'NJ': '🏗️ نيو جيرسي',
        'VA': '🏛️ فيرجينيا',
        'WA': '🌲 واشنطن',
        'AZ': '🌵 أريزونا',
        'MA': '📚 ماساتشوستس',
        'TN': '🎵 تينيسي'
    }
    
    # إنشاء صفوف من ولايتين
    row = []
    for state_code, name in state_names.items():
        is_enabled = states.get(state_code, True)
        status = "🟢" if is_enabled else "🔴"
        action = "disable" if is_enabled else "enable"
        
        button = InlineKeyboardButton(
            f"{status} {name}", 
            callback_data=f"toggle_state_socks_US_{state_code}_{action}"
        )
        
        row.append(button)
        if len(row) == 2:
            keyboard.append(row)
            row = []
    
    # إضافة أي أزرار متبقية
    if row:
        keyboard.append(row)
    
    keyboard.append([InlineKeyboardButton("🔙 رجوع", callback_data="manage_socks_countries")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "🇺🇸 إدارة ولايات أمريكا - السوكس\n\n"
        "🟢 = مفعل | 🔴 = معطل\n"
        "اضغط على الولاية لتغيير حالتها:",
        reply_markup=reply_markup
    )

async def handle_manage_static_us_states(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالجة إدارة ولايات أمريكا للستاتيك"""
    query = update.callback_query
    await query.answer()
    
    # الحصول على حالة الولايات لخدمات الستاتيك المختلفة
    residential_states = db.get_states_status('static', 'monthly_residential', 'US')
    verizon_states = db.get_states_status('static', 'monthly_verizon', 'US')
    
    keyboard = []
    
    # زر تشغيل/إيقاف جميع ولايات الستاتيك
    all_residential_enabled = all(residential_states.values()) if residential_states else True
    all_verizon_enabled = all(verizon_states.values()) if verizon_states else True
    all_enabled = all_residential_enabled and all_verizon_enabled
    
    toggle_all_text = "❌ إيقاف جميع ولايات الستاتيك" if all_enabled else "✅ تشغيل جميع ولايات الستاتيك"
    keyboard.append([InlineKeyboardButton(toggle_all_text, callback_data=f"toggle_all_static_us_states_{not all_enabled}")])
    
    # ولايات ريزيدنتال
    keyboard.append([InlineKeyboardButton("🏠 ولايات ريزيدنتال", callback_data="header_residential")])
    
    residential_state_names = {
        'NY': '🏙️ نيويورك',
        'AZ': '🌵 أريزونا', 
        'DE': '🏛️ ديلاوير',
        'VA': '🏛️ فيرجينيا',
        'WA': '🌲 واشنطن'
    }
    
    # أزرار ولايات ريزيدنتال
    row = []
    for state_code, name in residential_state_names.items():
        is_enabled = residential_states.get(state_code, True)
        status = "🟢" if is_enabled else "🔴"
        action = "disable" if is_enabled else "enable"
        
        button = InlineKeyboardButton(
            f"{status} {name}", 
            callback_data=f"toggle_state_static_residential_US_{state_code}_{action}"
        )
        
        row.append(button)
        if len(row) == 2:
            keyboard.append(row)
            row = []
    
    if row:
        keyboard.append(row)
    
    # ولايات فيريزون
    keyboard.append([InlineKeyboardButton("📱 ولايات Crocker", callback_data="header_verizon")])
    
    verizon_state_names = {
        'NY': '🏙️ نيويورك',
        'VA': '🏛️ فيرجينيا',
        'WA': '🌲 واشنطن',
        'MA': '🏛️ ماساتشوستس'
    }
    
    # أزرار ولايات فيريزون
    row = []
    for state_code, name in verizon_state_names.items():
        is_enabled = verizon_states.get(state_code, True)
        status = "🟢" if is_enabled else "🔴"
        action = "disable" if is_enabled else "enable"
        
        button = InlineKeyboardButton(
            f"{status} {name}", 
            callback_data=f"toggle_state_static_verizon_US_{state_code}_{action}"
        )
        
        row.append(button)
        if len(row) == 2:
            keyboard.append(row)
            row = []
    
    if row:
        keyboard.append(row)
    
    keyboard.append([InlineKeyboardButton("🔙 رجوع", callback_data="manage_static_countries")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "🇺🇸 إدارة ولايات أمريكا - الستاتيك\n\n"
        "🟢 = مفعل | 🔴 = معطل\n"
        "اضغط على الولاية لتغيير حالتها:",
        reply_markup=reply_markup
    )

# إنشاء معالجات المحادثة للبروكسيات المجانية

# معالج إدارة البروكسيات (المجانية والمدفوعة)
free_proxy_conv_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(handle_add_free_proxy, pattern="^add_free_proxy$"),
        CallbackQueryHandler(handle_delete_free_proxy, pattern="^delete_free_proxy$"),
    ],
    states={
        ADD_FREE_PROXY: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_free_proxy_message),
        ],
        DELETE_FREE_PROXY: [
            CallbackQueryHandler(handle_view_proxy_for_delete, pattern="^view_proxy_"),
            CallbackQueryHandler(handle_confirm_delete_proxy, pattern="^confirm_delete_"),
            CallbackQueryHandler(handle_delete_free_proxy, pattern="^delete_free_proxy$"),
        ],
    },
    fallbacks=[
        CallbackQueryHandler(handle_cancel_add_proxy, pattern="^cancel_add_proxy$"),
        CallbackQueryHandler(handle_back_to_manage_proxies, pattern="^back_to_manage_proxies$"),
        CallbackQueryHandler(handle_back_to_admin_menu, pattern="^back_to_admin_menu$"),
    ],
    allow_reentry=True
)

# معالج قبول طلبات شحن الرصيد مع إدخال قيمة الآدمن
recharge_approval_conv_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(handle_approve_recharge, pattern="^approve_recharge_")],
    states={
        ADMIN_RECHARGE_AMOUNT_INPUT: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_admin_recharge_amount_input)
        ]
    },
    fallbacks=[],
    allow_reentry=True
)

def setup_bot():
    """إعداد البوت وإضافة جميع المعالجات"""
    try:
        print("🔧 فحص إعدادات البوت...")
        
        if not TOKEN:
            print("❌ خطأ: لم يتم تعيين توكن البوت")
            return None
        
        print(f"✅ التوكن موجود: {TOKEN[:10]}...{TOKEN[-10:]}")
        
        print("🔧 بدء تهيئة البوت...")
        
        print("📊 تهيئة قاعدة البيانات...")
        print("⚠️ لم يتم العثور على تسجيل دخول أدمن سابق")
        
        # إنشاء ملفات المساعدة
        print("📁 إنشاء ملفات المساعدة...")
        create_requirements_file()
        print("✅ تم إنشاء ملفات المساعدة")
        
        # إنشاء تطبيق التيليجرام
        print("⚡ إنشاء تطبيق التيليجرام...")
        application = Application.builder().token(TOKEN).build()
        print("✅ تم إنشاء التطبيق بنجاح")
        
        # اختبار الاتصال
        print("🌐 اختبار الاتصال مع خوادم تيليجرام...")
        print("🌐 سيتم اختبار الاتصال عند بدء التشغيل...")
        
        # إضافة المعالجات
        print("🔧 إضافة معالجات الأوامر...")
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("about", handle_about_command))
        application.add_handler(CommandHandler("reset", handle_reset_command))
        application.add_handler(CommandHandler("cleanup", handle_cleanup_command))
        application.add_handler(CommandHandler("status", handle_status_command))

        print("🔧 إضافة معالجات المحادثات...")
        application.add_handler(admin_conv_handler)
        application.add_handler(password_change_conv_handler)
        application.add_handler(admin_functions_conv_handler)
        application.add_handler(process_order_conv_handler)
        application.add_handler(broadcast_conv_handler)
        application.add_handler(payment_conv_handler)
        application.add_handler(services_message_conv_handler)
        application.add_handler(exchange_rate_message_conv_handler)
        application.add_handler(free_proxy_conv_handler)
        application.add_handler(recharge_approval_conv_handler)
        
        print("🔧 إضافة معالجات الرسائل...")
        application.add_handler(CallbackQueryHandler(handle_callback_query))
        # تم إزالة معالج callback المتداخل للسوكس لحل المشكلة
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_messages))
        application.add_handler(MessageHandler(filters.PHOTO, handle_photo_messages))
        application.add_handler(MessageHandler(filters.Document.ALL, handle_document_messages))
        
        # إضافة معالج الأخطاء الشامل
        print("🔧 إضافة معالج الأخطاء الشامل...")
        application.add_error_handler(global_error_handler)
        
        # إضافة المهمة المجدولة لفحص الحظر المنتهي
        print("🔧 إضافة نظام فحص الحظر المنتهي...")
        try:
            # إضافة مهمة دورية كل 5 دقائق للفحص عن الحظر المنتهي
            application.job_queue.run_repeating(
                callback=lambda context: check_expired_bans_periodically(application), 
                interval=300,  # 5 دقائق بالثواني
                first=30,  # البدء بعد 30 ثانية من تشغيل البوت
                name='ban_checker'
            )
            print("✅ تم إضافة نظام فحص الحظر المنتهي (كل 5 دقائق)")
        except Exception as e:
            print(f"⚠️ تحذير: فشل في إضافة نظام فحص الحظر: {e}")
        
        # تهيئة نظام مراقبة الصحة
        # تم إزالة نظام مراقبة الصحة لحل مشكلة تسجيل الخروج التلقائي
        print("✅ تم تهيئة البوت بنجاح (مع نظام الحظر المتدرج)")
        
        print("✅ تم إضافة جميع المعالجات")
        print("📊 قاعدة البيانات جاهزة")
        print("⚡ البوت يعمل الآن!")
        print(f"🔑 التوكن: {TOKEN[:10]}...")
        print("💡 في انتظار الرسائل...")
        print("✅ البوت جاهز للتشغيل!")
        
        return application
        
    except Exception as e:
        print(f"❌ خطأ في إنشاء التطبيق أو الاتصال: {e}")
        import traceback
        traceback.print_exc()
        return None

def check_bot_lock():
    """فحص وإنشاء قفل البوت - يعمل على Windows و Unix/Linux"""
    lock_file = None
    
    if FCNTL_AVAILABLE:
        # نظام Unix/Linux - استخدام fcntl
        try:
            lock_file = open('bot.lock', 'w')
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            lock_file.write(str(os.getpid()))
            lock_file.flush()
            print("🔒 تم الحصول على قفل البوت بنجاح (Unix/Linux)")
            return lock_file
        except IOError:
            print("❌ يوجد بوت آخر يعمل بالفعل!")
            print("⚠️ يرجى إيقاف البوت الآخر أولاً أو استخدام:")
            print("   pkill -f proxy_bot.py")
            if lock_file:
                lock_file.close()
            return None
    else:
        # نظام Windows - استخدام ملف PID
        try:
            if os.path.exists('bot.lock'):
                # قراءة PID من الملف
                with open('bot.lock', 'r') as f:
                    old_pid = f.read().strip()
                
                # التحقق من وجود العملية
                if old_pid.isdigit():
                    try:
                        if platform.system() == "Windows":
                            # على Windows، نستخدم tasklist للتحقق من وجود العملية
                            result = subprocess.run(['tasklist', '/FI', f'PID eq {old_pid}'], 
                                                  capture_output=True, text=True)
                            if old_pid in result.stdout:
                                print("❌ يوجد بوت آخر يعمل بالفعل!")
                                print("⚠️ يرجى إيقاف البوت الآخر أولاً أو حذف ملف bot.lock")
                                return None
                        else:
                            # على Unix/Linux، نستخدم os.kill مع الإشارة 0
                            os.kill(int(old_pid), 0)
                            print("❌ يوجد بوت آخر يعمل بالفعل!")
                            print("⚠️ يرجى إيقاف البوت الآخر أولاً أو حذف ملف bot.lock")
                            return None
                    except (OSError, subprocess.SubprocessError):
                        # العملية غير موجودة، يمكننا المتابعة
                        pass
            
            # إنشاء ملف القفل الجديد
            lock_file = open('bot.lock', 'w')
            lock_file.write(str(os.getpid()))
            lock_file.flush()
            print("🔒 تم الحصول على قفل البوت بنجاح (Windows)")
            return lock_file
            
        except Exception as e:
            print(f"⚠️ تحذير: لا يمكن إنشاء قفل البوت: {e}")
            print("سيتم تشغيل البوت بدون قفل")
            return None

def cleanup_bot_lock(lock_file):
    """تنظيف قفل البوت"""
    if lock_file:
        try:
            if FCNTL_AVAILABLE:
                fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)
            lock_file.close()
            os.unlink('bot.lock')
            print("🔓 تم تحرير قفل البوت")
        except:
            pass

# متغير عالمي لحفظ رسالة الخدمات
SERVICES_MESSAGE = {
    'ar': 'هذه رسالة الخدمات الافتراضية. يمكن للإدارة تعديلها.',
    'en': 'This is the default services message. Admin can modify it.'
}

# متغير عالمي لحفظ رسالة سعر الصرف
EXCHANGE_RATE_MESSAGE = {
    'ar': 'هذه رسالة سعر الصرف الافتراضية. يمكن للإدارة تعديلها.',
    'en': 'This is the default exchange rate message. Admin can modify it.'
}

async def handle_services(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالجة زر المزيد من الخدمات"""
    user_id = update.effective_user.id
    language = get_user_language(user_id)
    
    message = "اختر ما تريد من القائمة" if language == 'ar' else "Choose what you want from the menu"
    
    keyboard = [
        [InlineKeyboardButton(
            "📋 لمحة عن خدمات البوت" if language == 'ar' else "📋 About Bot Services", 
            callback_data="show_bot_services"
        )],
        [InlineKeyboardButton(
            "💱 سعر الصرف" if language == 'ar' else "💱 Exchange Rate", 
            callback_data="show_exchange_rate"
        )]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(message, reply_markup=reply_markup)


async def handle_show_bot_services(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالجة زر لمحة عن خدمات البوت - Fun1 الأصلية"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    language = get_user_language(user_id)
    
    # الحصول على رسالة الخدمات من قاعدة البيانات أو استخدام الافتراضية
    try:
        result = db.execute_query("SELECT value FROM settings WHERE key = ?", (f'services_message_{language}',))
        services_msg = result[0][0] if result else SERVICES_MESSAGE[language]
    except:
        services_msg = SERVICES_MESSAGE[language]
    
    await query.edit_message_text(services_msg, parse_mode='Markdown')


async def handle_show_exchange_rate(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالجة زر سعر الصرف"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    language = get_user_language(user_id)
    
    # الحصول على رسالة سعر الصرف من قاعدة البيانات أو استخدام الافتراضية
    try:
        result = db.execute_query("SELECT value FROM settings WHERE key = ?", (f'exchange_rate_message_{language}',))
        exchange_msg = result[0][0] if result else EXCHANGE_RATE_MESSAGE[language]
    except:
        exchange_msg = EXCHANGE_RATE_MESSAGE[language]
    
    await query.edit_message_text(exchange_msg, parse_mode='Markdown')

# وظائف إدارة المستخدم المتقدمة الجديدة

async def handle_ban_user_action(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالجة حظر المستخدم"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.data.split("_")[-1]
    user_data = context.user_data.get('selected_user_data')
    
    if not user_data:
        await query.edit_message_text("❌ خطأ: بيانات المستخدم غير متوفرة")
        return
    
    # تأكيد الحظر
    keyboard = [
        [
            InlineKeyboardButton("✅ نعم، حظر المستخدم", callback_data=f"confirm_ban_{user_id}"),
            InlineKeyboardButton("❌ إلغاء", callback_data=f"back_to_profile_{user_id}")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    message = f"""⚠️ **تأكيد حظر المستخدم**

📋 **المستخدم:** {user_data[2]} {user_data[3]}
🆔 **المعرف:** `{user_id}`

🚫 **هل أنت متأكد من حظر هذا المستخدم؟**

⚠️ **تحذير:** المستخدم المحظور لن يتمكن من استخدام البوت نهائياً"""
    
    await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')

async def handle_unban_user_action(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالجة فك حظر المستخدم"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.data.split("_")[-1]
    user_data = context.user_data.get('selected_user_data')
    
    if not user_data:
        await query.edit_message_text("❌ خطأ: بيانات المستخدم غير متوفرة")
        return
    
    # تأكيد فك الحظر
    keyboard = [
        [
            InlineKeyboardButton("✅ نعم، فك الحظر", callback_data=f"confirm_unban_{user_id}"),
            InlineKeyboardButton("❌ إلغاء", callback_data=f"back_to_profile_{user_id}")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    message = f"""✅ **تأكيد فك حظر المستخدم**

📋 **المستخدم:** {user_data[2]} {user_data[3]}
🆔 **المعرف:** `{user_id}`

🔓 **هل أنت متأكد من فك حظر هذا المستخدم؟**

ℹ️ **ملاحظة:** المستخدم سيتمكن من استخدام البوت مرة أخرى"""
    
    await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')

async def handle_remove_temp_ban_action(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالجة رفع الحظر المؤقت بسبب العمليات التخريبية"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.data.split("_")[-1]
    user_data = context.user_data.get('selected_user_data')
    
    if not user_data:
        await query.edit_message_text("❌ خطأ: بيانات المستخدم غير متوفرة")
        return
    
    # تأكيد رفع الحظر المؤقت
    keyboard = [
        [
            InlineKeyboardButton("✅ نعم، رفع الحظر المؤقت", callback_data=f"confirm_remove_temp_ban_{user_id}"),
            InlineKeyboardButton("❌ إلغاء", callback_data=f"back_to_profile_{user_id}")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    message = f"""🛠️ **رفع الحظر المؤقت**

📋 **المستخدم:** {user_data[2]} {user_data[3]}
🆔 **المعرف:** `{user_id}`

🔧 **رفع الحظر المؤقت بسبب العمليات التخريبية**

ℹ️ **هذا الخيار مخصص للمستخدمين المحظورين مؤقتاً بسبب:**
• النقر المتكرر أو السريع
• محاولة استغلال النظام
• أنشطة مشبوهة أخرى

✅ **سيتم إزالة الحظر المؤقت وإعادة تعيين عداد المخالفات**"""
    
    await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')

async def handle_add_points_action(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالجة إضافة النقاط"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.data.split("_")[-1]
    user_data = context.user_data.get('selected_user_data')
    
    if not user_data:
        await query.edit_message_text("❌ خطأ: بيانات المستخدم غير متوفرة")
        return
    
    # حفظ بيانات المستخدم المحدد
    context.user_data['target_user_id'] = user_id
    context.user_data['points_action'] = 'add'
    
    current_balance = float(user_data[6]) if user_data[6] else 0.0
    
    message = f"""➕ **إضافة نقاط للمستخدم**

📋 **المستخدم:** {user_data[2]} {user_data[3]}
🆔 **المعرف:** `{user_id}`
💳 **الرصيد الحالي:** `${current_balance:.2f}`

⚠️ **تنبيه مهم:** أدخل القيمة بالنقاط وليس بالدولار!

💰 **أدخل عدد النقاط المراد إضافتها:**
(مثال: 100 لإضافة 100 نقطة)"""
    
    await query.edit_message_text(message, parse_mode='Markdown')
    return ADD_POINTS_AMOUNT

async def handle_subtract_points_action(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالجة خصم النقاط"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.data.split("_")[-1]
    user_data = context.user_data.get('selected_user_data')
    
    if not user_data:
        await query.edit_message_text("❌ خطأ: بيانات المستخدم غير متوفرة")
        return
    
    # حفظ بيانات المستخدم المحدد
    context.user_data['target_user_id'] = user_id
    context.user_data['points_action'] = 'subtract'
    
    current_balance = float(user_data[6]) if user_data[6] else 0.0
    
    message = f"""➖ **خصم نقاط من المستخدم**

📋 **المستخدم:** {user_data[2]} {user_data[3]}
🆔 **المعرف:** `{user_id}`
💳 **الرصيد الحالي:** `${current_balance:.2f}`

⚠️ **تنبيه مهم:** أدخل القيمة بالنقاط وليس بالدولار!

💸 **أدخل عدد النقاط المراد خصمها:**
(مثال: 50 لخصم 50 نقطة)"""
    
    await query.edit_message_text(message, parse_mode='Markdown')
    return SUBTRACT_POINTS_AMOUNT

async def handle_add_referral_action(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالجة إدراج إحالة جديدة"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.data.split("_")[-1]
    user_data = context.user_data.get('selected_user_data')
    
    if not user_data:
        await query.edit_message_text("❌ خطأ: بيانات المستخدم غير متوفرة")
        return
    
    # حفظ بيانات المستخدم المحدد
    context.user_data['target_user_id'] = user_id
    
    message = f"""➕ **إدراج إحالة جديدة**

📋 **المُحيل:** {user_data[2]} {user_data[3]}
🆔 **معرف المُحيل:** `{user_id}`

👤 **أدخل اسم المستخدم أو المعرف للمستخدم المُحال:**
(مثال: @username أو 123456789)

ℹ️ **ملاحظة:** سيتم ربط هذا المستخدم كإحالة من المُحيل المحدد"""
    
    await query.edit_message_text(message, parse_mode='Markdown')
    return ADD_REFERRAL_USERNAME

async def handle_delete_referral_action(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالجة حذف إحالة محددة مع عرض أسماء المحالين"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.data.split("_")[-1]
    user_data = context.user_data.get('selected_user_data')
    
    if not user_data:
        await query.edit_message_text("❌ خطأ: بيانات المستخدم غير متوفرة")
        return
    
    # جلب قائمة المستخدمين المحالين
    try:
        referrals = db.execute_query("""
            SELECT u.user_id, u.username, u.first_name, u.last_name, r.referred_at
            FROM referrals r
            JOIN users u ON r.referred_id = u.user_id
            WHERE r.referrer_id = ?
            ORDER BY r.referred_at DESC
        """, (user_id,))
        
        if not referrals:
            await query.edit_message_text(f"""❌ **لا توجد إحالات**

📋 **المستخدم:** {user_data[2]} {user_data[3]}
🆔 **المعرف:** `{user_id}`

🔍 **هذا المستخدم لا يملك أي إحالات ليتم حذفها**""", parse_mode='Markdown')
            return
        
        # إنشاء قائمة بالمحالين
        keyboard = []
        for i, referral in enumerate(referrals[:10]):  # أول 10 إحالات
            ref_id, username, first_name, last_name, referred_at = referral
            display_name = f"{first_name or ''} {last_name or ''}".strip() or f"مستخدم {ref_id}"
            username_text = f"@{username}" if username else "بدون اسم مستخدم"
            
            keyboard.append([
                InlineKeyboardButton(
                    f"🗑️ {display_name} ({username_text})",
                    callback_data=f"confirm_delete_referral_{user_id}_{ref_id}"
                )
            ])
        
        keyboard.append([
            InlineKeyboardButton("🔙 رجوع للملف", callback_data=f"back_to_profile_{user_id}")
        ])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        message = f"""❌ **حذف إحالة محددة**

📋 **المُحيل:** {user_data[2]} {user_data[3]}
🆔 **المعرف:** `{user_id}`

👥 **اختر المستخدم المُحال المراد حذفه:**
(عدد الإحالات: {len(referrals)})"""
        
        await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')
        
    except Exception as e:
        await query.edit_message_text(f"❌ خطأ في جلب الإحالات: {str(e)}")

async def handle_reset_referral_balance_action(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالجة تصفير رصيد الإحالة فقط"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.data.split("_")[-1]
    user_data = context.user_data.get('selected_user_data')
    
    if not user_data:
        await query.edit_message_text("❌ خطأ: بيانات المستخدم غير متوفرة")
        return
    
    referral_earnings = float(user_data[5]) if user_data[5] else 0.0
    
    # تأكيد تصفير رصيد الإحالة
    keyboard = [
        [
            InlineKeyboardButton("✅ نعم، تصفير رصيد الإحالة", callback_data=f"confirm_reset_referral_balance_{user_id}"),
            InlineKeyboardButton("❌ إلغاء", callback_data=f"back_to_profile_{user_id}")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    message = f"""🗑️ **تصفير رصيد الإحالة**

📋 **المستخدم:** {user_data[2]} {user_data[3]}
🆔 **المعرف:** `{user_id}`
💰 **رصيد الإحالة الحالي:** `${referral_earnings:.2f}`

⚠️ **هل أنت متأكد من تصفير رصيد الإحالة؟**

ℹ️ **ملاحظة:** سيتم تصفير رصيد الإحالة فقط وليس حذف الإحالات نفسها"""
    
    await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')

async def handle_single_user_broadcast_action(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالجة إرسال رسالة نصية للمستخدم"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.data.split("_")[-1]
    user_data = context.user_data.get('selected_user_data')
    
    if not user_data:
        await query.edit_message_text("❌ خطأ: بيانات المستخدم غير متوفرة")
        return
    
    # حفظ بيانات المستخدم المحدد
    context.user_data['target_user_id'] = user_id
    context.user_data['broadcast_type'] = 'text'
    
    message = f"""📝 **رسالة نصية للمستخدم**

📋 **المستخدم:** {user_data[2]} {user_data[3]}
🆔 **المعرف:** `{user_id}`
📱 **اسم المستخدم:** @{user_data[1] or 'غير محدد'}

💬 **أدخل الرسالة النصية:**"""
    
    await query.edit_message_text(message, parse_mode='Markdown')
    return SINGLE_USER_BROADCAST_MESSAGE

async def handle_single_user_broadcast_photo_action(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالجة إرسال رسالة مع صورة للمستخدم"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.data.split("_")[-1]
    user_data = context.user_data.get('selected_user_data')
    
    if not user_data:
        await query.edit_message_text("❌ خطأ: بيانات المستخدم غير متوفرة")
        return
    
    # حفظ بيانات المستخدم المحدد
    context.user_data['target_user_id'] = user_id
    context.user_data['broadcast_type'] = 'photo'
    
    message = f"""🖼️ **رسالة مع صورة للمستخدم**

📋 **المستخدم:** {user_data[2]} {user_data[3]}
🆔 **المعرف:** `{user_id}`
📱 **اسم المستخدم:** @{user_data[1] or 'غير محدد'}

📷 **أرسل الصورة مع النص (اختياري):**"""
    
    await query.edit_message_text(message, parse_mode='Markdown')
    return SINGLE_USER_BROADCAST_MESSAGE

async def handle_quick_message_action(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالجة الرسائل السريعة (قوالب جاهزة)"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.data.split("_")[-1]
    user_data = context.user_data.get('selected_user_data')
    
    if not user_data:
        await query.edit_message_text("❌ خطأ: بيانات المستخدم غير متوفرة")
        return
    
    # قوالب الرسائل السريعة
    keyboard = [
        [
            InlineKeyboardButton("🎉 تهنئة", callback_data=f"quick_template_congratulation_{user_id}"),
            InlineKeyboardButton("⚠️ تحذير", callback_data=f"quick_template_warning_{user_id}")
        ],
        [
            InlineKeyboardButton("ℹ️ إشعار", callback_data=f"quick_template_notification_{user_id}"),
            InlineKeyboardButton("🛠️ صيانة", callback_data=f"quick_template_maintenance_{user_id}")
        ],
        [
            InlineKeyboardButton("💰 عرض خاص", callback_data=f"quick_template_offer_{user_id}"),
            InlineKeyboardButton("📞 دعم فني", callback_data=f"quick_template_support_{user_id}")
        ],
        [
            InlineKeyboardButton("🔙 رجوع للملف", callback_data=f"back_to_profile_{user_id}")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    message = f"""⚡ **رسالة سريعة (قوالب جاهزة)**

📋 **المستخدم:** {user_data[2]} {user_data[3]}
🆔 **المعرف:** `{user_id}`

📝 **اختر نوع الرسالة السريعة:**"""
    
    await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')

async def handle_important_notice_action(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالجة الإشعارات الهامة"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.data.split("_")[-1]
    user_data = context.user_data.get('selected_user_data')
    
    if not user_data:
        await query.edit_message_text("❌ خطأ: بيانات المستخدم غير متوفرة")
        return
    
    # حفظ بيانات المستخدم المحدد
    context.user_data['target_user_id'] = user_id
    context.user_data['broadcast_type'] = 'important'
    
    message = f"""📢 **إشعار هام للمستخدم**

📋 **المستخدم:** {user_data[2]} {user_data[3]}
🆔 **المعرف:** `{user_id}`
📱 **اسم المستخدم:** @{user_data[1] or 'غير محدد'}

⚠️ **أدخل الإشعار الهام:**
(سيتم إرساله بتنسيق خاص ليبرز أهميته)"""
    
    await query.edit_message_text(message, parse_mode='Markdown')
    return SINGLE_USER_BROADCAST_MESSAGE

async def handle_back_to_user_profile(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """العودة لملف المستخدم الشخصي"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.data.split("_")[-1]
    user_data = context.user_data.get('selected_user_data')
    
    if not user_data:
        await query.edit_message_text("❌ خطأ: بيانات المستخدم غير متوفرة")
        return
    
    # إعادة عرض ملف المستخدم
    await show_user_profile_detailed(update, context, user_id, user_data)

# دوال التأكيد الجديدة لإدارة المستخدم المتقدمة

async def handle_confirm_ban_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """تأكيد حظر المستخدم"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.data.split("_")[-1]
    user_data = context.user_data.get('selected_user_data')
    
    if not user_data:
        await query.edit_message_text("❌ خطأ: بيانات المستخدم غير متوفرة")
        return
    
    try:
        # إضافة المستخدم لقائمة المحظورين
        db.execute_query("""
            INSERT OR REPLACE INTO banned_users (user_id, username, ban_reason, banned_at, banned_by)
            VALUES (?, ?, ?, datetime('now'), ?)
        """, (user_id, user_data[1], "حظر من الأدمن", update.effective_user.id))
        
        # إرسال إشعار للمستخدم المحظور
        try:
            await context.bot.send_message(
                chat_id=user_id,
                text="🚫 **تم حظرك من استخدام البوت**\n\nللاستفسار تواصل مع الإدارة",
                parse_mode='Markdown'
            )
        except:
            pass  # المستخدم قد يكون حظر البوت
        
        success_message = f"""✅ **تم حظر المستخدم بنجاح**

📋 **المستخدم:** {user_data[2]} {user_data[3]}
🆔 **المعرف:** `{user_id}`
📱 **اسم المستخدم:** @{user_data[1] or 'غير محدد'}

🚫 **الحالة:** محظور نهائياً
📅 **تاريخ الحظر:** {datetime.now().strftime('%Y-%m-%d %H:%M')}

✅ **تم إرسال إشعار للمستخدم بالحظر**"""
        
        keyboard = [
            [InlineKeyboardButton("🔙 رجوع لقائمة الأدمن", callback_data="back_to_admin_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(success_message, reply_markup=reply_markup, parse_mode='Markdown')
        
    except Exception as e:
        await query.edit_message_text(f"❌ خطأ في حظر المستخدم: {str(e)}")

async def handle_confirm_unban_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """تأكيد فك حظر المستخدم"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.data.split("_")[-1]
    user_data = context.user_data.get('selected_user_data')
    
    if not user_data:
        await query.edit_message_text("❌ خطأ: بيانات المستخدم غير متوفرة")
        return
    
    try:
        # إزالة المستخدم من قائمة المحظورين
        db.execute_query("DELETE FROM banned_users WHERE user_id = ?", (user_id,))
        
        # إزالة الحظر المؤقت أيضاً إن وجد
        if user_id in TEMP_BANNED_USERS:
            del TEMP_BANNED_USERS[user_id]
        
        # إرسال إشعار للمستخدم
        try:
            await context.bot.send_message(
                chat_id=user_id,
                text="✅ **تم فك حظرك من البوت**\n\nيمكنك الآن استخدام البوت بشكل طبيعي\nمرحباً بك مرة أخرى! 🎉",
                parse_mode='Markdown'
            )
        except:
            pass
        
        success_message = f"""✅ **تم فك حظر المستخدم بنجاح**

📋 **المستخدم:** {user_data[2]} {user_data[3]}
🆔 **المعرف:** `{user_id}`
📱 **اسم المستخدم:** @{user_data[1] or 'غير محدد'}

🔓 **الحالة:** تم فك الحظر
📅 **تاريخ فك الحظر:** {datetime.now().strftime('%Y-%m-%d %H:%M')}

✅ **تم إرسال إشعار للمستخدم بفك الحظر**"""
        
        keyboard = [
            [InlineKeyboardButton("🔙 رجوع لقائمة الأدمن", callback_data="back_to_admin_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(success_message, reply_markup=reply_markup, parse_mode='Markdown')
        
    except Exception as e:
        await query.edit_message_text(f"❌ خطأ في فك حظر المستخدم: {str(e)}")

async def handle_confirm_remove_temp_ban(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """تأكيد رفع الحظر المؤقت"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.data.split("_")[-1]
    user_data = context.user_data.get('selected_user_data')
    
    if not user_data:
        await query.edit_message_text("❌ خطأ: بيانات المستخدم غير متوفرة")
        return
    
    try:
        # رفع الحظر المؤقت
        if user_id in TEMP_BANNED_USERS:
            del TEMP_BANNED_USERS[user_id]
            temp_ban_removed = True
        else:
            temp_ban_removed = False
        
        # إزالة عداد النقرات السريعة
        if user_id in USER_CLICK_COUNT:
            del USER_CLICK_COUNT[user_id]
        
        if user_id in USER_LAST_CLICK:
            del USER_LAST_CLICK[user_id]
        
        # إرسال إشعار للمستخدم
        try:
            await context.bot.send_message(
                chat_id=user_id,
                text="🛠️ **تم رفع الحظر المؤقت**\n\nتم إزالة الحظر المؤقت وإعادة تعيين عداد المخالفات\nيمكنك الآن استخدام البوت بشكل طبيعي 🎉",
                parse_mode='Markdown'
            )
        except:
            pass
        
        status = "تم رفع الحظر المؤقت" if temp_ban_removed else "لم يكن محظوراً مؤقتاً"
        
        success_message = f"""🛠️ **رفع الحظر المؤقت**

📋 **المستخدم:** {user_data[2]} {user_data[3]}
🆔 **المعرف:** `{user_id}`
📱 **اسم المستخدم:** @{user_data[1] or 'غير محدد'}

🔧 **الحالة:** {status}
📅 **تاريخ المعالجة:** {datetime.now().strftime('%Y-%m-%d %H:%M')}

✅ **تم إعادة تعيين عداد المخالفات**
✅ **تم إرسال إشعار للمستخدم**"""
        
        keyboard = [
            [InlineKeyboardButton("🔙 رجوع لقائمة الأدمن", callback_data="back_to_admin_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(success_message, reply_markup=reply_markup, parse_mode='Markdown')
        
    except Exception as e:
        await query.edit_message_text(f"❌ خطأ في رفع الحظر المؤقت: {str(e)}")

async def handle_confirm_reset_referral_balance(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """تأكيد تصفير رصيد الإحالة"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.data.split("_")[-1]
    user_data = context.user_data.get('selected_user_data')
    
    if not user_data:
        await query.edit_message_text("❌ خطأ: بيانات المستخدم غير متوفرة")
        return
    
    try:
        old_balance = float(user_data[5]) if user_data[5] else 0.0
        
        # تصفير رصيد الإحالة فقط
        db.execute_query("UPDATE users SET referral_balance = 0 WHERE user_id = ?", (user_id,))
        
        success_message = f"""🗑️ **تم تصفير رصيد الإحالة بنجاح**

📋 **المستخدم:** {user_data[2]} {user_data[3]}
🆔 **المعرف:** `{user_id}`

💰 **الرصيد السابق:** `${old_balance:.2f}`
💰 **الرصيد الحالي:** `$0.00`

✅ **تم تصفير رصيد الإحالة فقط**
ℹ️ **الإحالات نفسها لم يتم حذفها**"""
        
        keyboard = [
            [InlineKeyboardButton("🔙 رجوع لقائمة الأدمن", callback_data="back_to_admin_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(success_message, reply_markup=reply_markup, parse_mode='Markdown')
        
    except Exception as e:
        await query.edit_message_text(f"❌ خطأ في تصفير رصيد الإحالة: {str(e)}")

async def handle_confirm_delete_referral(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """تأكيد حذف إحالة محددة"""
    query = update.callback_query
    await query.answer()
    
    # استخراج معرف المُحيل ومعرف المُحال
    parts = query.data.split("_")
    referrer_id = parts[-2]
    referred_id = parts[-1]
    
    try:
        # جلب معلومات المستخدم المُحال
        referred_user = db.execute_query("""
            SELECT username, first_name, last_name 
            FROM users WHERE user_id = ?
        """, (referred_id,))
        
        if not referred_user:
            await query.edit_message_text("❌ خطأ: المستخدم المُحال غير موجود")
            return
        
        referred_username, referred_first, referred_last = referred_user[0]
        referred_name = f"{referred_first or ''} {referred_last or ''}".strip() or f"مستخدم {referred_id}"
        
        # حذف الإحالة
        db.execute_query("DELETE FROM referrals WHERE referrer_id = ? AND referred_id = ?", 
                        (referrer_id, referred_id))
        
        success_message = f"""❌ **تم حذف الإحالة بنجاح**

📋 **المُحيل:** معرف `{referrer_id}`
👤 **المُحال المحذوف:** {referred_name}
🆔 **معرف المُحال:** `{referred_id}`
📱 **اسم المستخدم:** @{referred_username or 'غير محدد'}

✅ **تم حذف الإحالة من قاعدة البيانات**
📅 **تاريخ الحذف:** {datetime.now().strftime('%Y-%m-%d %H:%M')}"""
        
        keyboard = [
            [InlineKeyboardButton("🔙 رجوع لقائمة الأدمن", callback_data="back_to_admin_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(success_message, reply_markup=reply_markup, parse_mode='Markdown')
        
    except Exception as e:
        await query.edit_message_text(f"❌ خطأ في حذف الإحالة: {str(e)}")

async def handle_quick_template_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالجة اختيار قالب الرسالة السريعة"""
    query = update.callback_query
    await query.answer()
    
    # استخراج نوع القالب ومعرف المستخدم
    parts = query.data.split("_")
    template_type = parts[2]  # congratulation, warning, etc.
    user_id = parts[-1]
    
    user_data = context.user_data.get('selected_user_data')
    
    if not user_data:
        await query.edit_message_text("❌ خطأ: بيانات المستخدم غير متوفرة")
        return
    
    # قوالب الرسائل السريعة
    templates = {
        'congratulation': "🎉 **تهنئة!**\n\nنهنئك على استخدامك المميز لخدماتنا!\nشكراً لك على ثقتك بنا 💫",
        'warning': "⚠️ **تحذير هام**\n\nيرجى الالتزام بشروط الاستخدام\nوتجنب أي أنشطة مخالفة للقوانين",
        'notification': "ℹ️ **إشعار**\n\nنود إعلامك بتحديث في خدماتنا\nيرجى مراجعة القائمة الرئيسية للتفاصيل",
        'maintenance': "🛠️ **إشعار صيانة**\n\nسيتم إجراء صيانة دورية على النظام\nشكراً لتفهمكم",
        'offer': "💰 **عرض خاص**\n\nلديك عرض خاص متاح الآن!\nاستفد من الخصومات المتاحة",
        'support': "📞 **دعم فني**\n\nفريق الدعم الفني جاهز لمساعدتك\nلا تتردد في التواصل معنا"
    }
    
    template_message = templates.get(template_type, "📝 رسالة عامة")
    
    try:
        # إرسال الرسالة للمستخدم
        await context.bot.send_message(
            chat_id=user_id,
            text=template_message,
            parse_mode='Markdown'
        )
        
        success_message = f"""✅ **تم إرسال الرسالة السريعة بنجاح**

📋 **المستخدم:** {user_data[2]} {user_data[3]}
🆔 **المعرف:** `{user_id}`
📝 **نوع الرسالة:** {template_type}

📤 **تم إرسال الرسالة بنجاح**
📅 **وقت الإرسال:** {datetime.now().strftime('%Y-%m-%d %H:%M')}"""
        
        keyboard = [
            [InlineKeyboardButton("🔙 رجوع لقائمة الأدمن", callback_data="back_to_admin_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(success_message, reply_markup=reply_markup, parse_mode='Markdown')
        
    except Exception as e:
        await query.edit_message_text(f"❌ خطأ في إرسال الرسالة: {str(e)}")


async def handle_manage_detailed_static(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالجة الإدارة التفصيلية لخدمة ستاتيك محددة"""
    query = update.callback_query
    await query.answer()
    
    callback_data = query.data
    service_type = callback_data.replace("manage_detailed_static_", "")
    
    # معلومات الخدمات
    service_info = {
        'monthly_residential': {'name': '🏢 ريزيدنتال', 'price': '6$'},
        'monthly_verizon': {'name': '🏠 ريزيدنتال Crocker', 'price': '4$'},
        'isp_att': {'name': '🌐 ISP', 'price': '3$'},
        'datacenter': {'name': '🔧 Datacenter Proxy', 'price': '12$'}
    }
    
    if service_type not in service_info:
        await query.edit_message_text("❌ خدمة غير صحيحة")
        return
    
    info = service_info[service_type]
    is_enabled = db.get_service_status('static', service_type)
    
    # الحصول على إحصائيات الخدمة
    service_stats = db.get_service_statistics(service_type)
    
    keyboard = []
    
    # تبديل حالة الخدمة
    status_text = "🟢 مفعل" if is_enabled else "🔴 معطل"
    action_text = "إيقاف" if is_enabled else "تشغيل"
    action = "disable" if is_enabled else "enable"
    
    keyboard.append([InlineKeyboardButton(
        f"{action_text} الخدمة", 
        callback_data=f"toggle_static_{service_type}_{action}"
    )])
    
    # إدارة حسب المواقع
    if service_type in ['monthly_residential', 'monthly_verizon']:
        keyboard.append([InlineKeyboardButton(
            f"🌍 إدارة دول {info['name']}", 
            callback_data=f"manage_countries_{service_type}"
        )])
        keyboard.append([InlineKeyboardButton(
            f"🏛️ إدارة الولايات الأمريكية", 
            callback_data=f"manage_states_{service_type}"
        )])
    
    # خيارات متقدمة
    keyboard.append([InlineKeyboardButton(
        "📊 إحصائيات مفصلة", 
        callback_data=f"detailed_stats_{service_type}"
    )])
    
    keyboard.append([InlineKeyboardButton(
        "🔧 إعدادات متقدمة", 
        callback_data=f"advanced_settings_{service_type}"
    )])
    
    # العودة
    keyboard.append([InlineKeyboardButton("🔙 رجوع", callback_data="manage_static_services")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    stats_text = f"""
📈 **الطلبات الإجمالية:** {service_stats.get('total_orders', 0)}
📈 **الطلبات اليوم:** {service_stats.get('today_orders', 0)}
💰 **الإيرادات الإجمالية:** ${service_stats.get('total_revenue', 0)}
""" if service_stats else "📊 لا توجد إحصائيات متاحة"
    
    await query.edit_message_text(
        f"⚙️ **إدارة تفصيلية: {info['name']}**\n\n"
        f"💰 **السعر:** {info['price']}\n"
        f"📊 **الحالة:** {status_text}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{stats_text}"
        f"━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"اختر الإجراء المطلوب:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

# دوال معالجة أزرار إدارة المستخدمين المتقدمة
async def handle_back_to_user_profile(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """العودة لملف المستخدم"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.data.split("_")[-1]
    user_data = context.user_data.get('selected_user_data')
    
    if not user_data:
        # إعادة البحث عن بيانات المستخدم
        user_result = db.execute_query("SELECT * FROM users WHERE user_id = ?", (user_id,))
        if not user_result:
            await query.edit_message_text("❌ خطأ: بيانات المستخدم غير متوفرة")
            return
        user_data = user_result[0]
        context.user_data['selected_user_data'] = user_data
    
    # إعادة عرض ملف المستخدم
    await display_user_profile(query, user_data, context)

async def display_user_profile(query, user_data, context):
    """عرض ملف المستخدم"""
    user_id = user_data[0]
    current_balance = float(user_data[6]) if user_data[6] else 0.0
    referral_earned = float(user_data[5]) if user_data[5] else 0.0
    
    # الحصول على إحصائيات محدثة
    successful_orders = db.execute_query(
        "SELECT COUNT(*), SUM(payment_amount) FROM orders WHERE user_id = ? AND status = 'completed'",
        (user_id,)
    )[0]
    
    referral_count = db.execute_query(
        "SELECT COUNT(*) FROM referrals WHERE referrer_id = ?", (user_id,)
    )[0][0]
    
    status_text = "🟢 نشط" if current_balance > 0 or successful_orders[0] > 0 else "🟡 غير نشط"
    
    report = f"""📊 ملف المستخدم المحدث

👤 **البيانات الشخصية**
• الاسم: {user_data[2]} {user_data[3]}
• اسم المستخدم: @{user_data[1] or 'غير محدد'}  
• المعرف: `{user_id}`
• الحالة: {status_text}

💰 **النظام المالي**
• الرصيد الحالي: `${current_balance:.2f}`
• رصيد الإحالات: `${referral_earned:.2f}`

📈 **إحصائيات الطلبات**
• الطلبات الناجحة: `{successful_orders[0]}` (${successful_orders[1] or 0:.2f})
• عدد المُحالين: `{referral_count}` شخص"""
    
    keyboard = [
        [
            InlineKeyboardButton("👤 إدارة المستخدم", callback_data=f"manage_user_{user_id}"),
            InlineKeyboardButton("💰 إدارة النقاط", callback_data=f"manage_points_{user_id}")
        ],
        [
            InlineKeyboardButton("📢 بث لهذا المستخدم", callback_data=f"broadcast_user_{user_id}"),
            InlineKeyboardButton("👥 إدارة الإحالات", callback_data=f"manage_referrals_{user_id}")
        ],
        [
            InlineKeyboardButton("💬 انتقال للمحادثة", url=f"tg://user?id={user_id}"),
            InlineKeyboardButton("📊 تقارير مفصلة", callback_data=f"detailed_reports_{user_id}")
        ],
        [
            InlineKeyboardButton("🔙 رجوع لقائمة الأدمن", callback_data="back_to_admin_menu")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(report, reply_markup=reply_markup, parse_mode='Markdown')

async def handle_show_referred_action(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """عرض قائمة المُحالين"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.data.split("_")[-1]
    
    # الحصول على قائمة المُحالين
    referrals = db.execute_query("""
        SELECT u.user_id, u.first_name, u.last_name, u.username, r.created_at
        FROM referrals r
        JOIN users u ON r.referred_id = u.user_id
        WHERE r.referrer_id = ?
        ORDER BY r.created_at DESC
    """, (user_id,))
    
    if not referrals:
        message = f"👥 **قائمة المُحالين**\n\n❌ لا يوجد مستخدمون محالون"
    else:
        referral_list = []
        for i, (ref_id, fname, lname, username, created_at) in enumerate(referrals[:10], 1):
            name = f"{fname} {lname}".strip()
            username_text = f"@{username}" if username else "لا يوجد"
            referral_list.append(f"{i}. **{name}** ({username_text})\n   • المعرف: `{ref_id}`\n   • تاريخ الإحالة: {created_at[:10]}")
        
        total_count = len(referrals)
        message = f"👥 **قائمة المُحالين** (إجمالي: {total_count})\n\n" + "\n\n".join(referral_list)
        
        if total_count > 10:
            message += f"\n\n📋 *عرض أول 10 من أصل {total_count} محال*"
    
    keyboard = [[InlineKeyboardButton("🔙 رجوع لإدارة الإحالات", callback_data=f"manage_referrals_{user_id}")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')

async def handle_referral_earnings_action(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """عرض سجل أرباح الإحالات"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.data.split("_")[-1]
    user_data = context.user_data.get('selected_user_data')
    
    if not user_data:
        await query.edit_message_text("❌ خطأ: بيانات المستخدم غير متوفرة")
        return
    
    # الحصول على سجل المعاملات المالية للإحالات
    transactions = db.execute_query("""
        SELECT transaction_type, amount, created_at, description
        FROM credits_transactions 
        WHERE user_id = ? AND transaction_type LIKE '%referral%'
        ORDER BY created_at DESC LIMIT 10
    """, (user_id,))
    
    referral_earnings = float(user_data[5]) if user_data[5] else 0.0
    
    if not transactions:
        message = f"💰 **سجل أرباح الإحالات**\n\n• إجمالي الأرباح: `${referral_earnings:.2f}`\n\n❌ لا توجد معاملات مسجلة"
    else:
        transaction_list = []
        for trans_type, amount, created_at, desc in transactions:
            date = created_at[:10] if created_at else "غير معروف"
            transaction_list.append(f"• **+${amount:.2f}** - {date}\n  {desc or 'مكافأة إحالة'}")
        
        message = f"💰 **سجل أرباح الإحالات**\n\n• إجمالي الأرباح: `${referral_earnings:.2f}`\n\n📊 **آخر المعاملات:**\n\n" + "\n\n".join(transaction_list)
    
    keyboard = [[InlineKeyboardButton("🔙 رجوع لإدارة الإحالات", callback_data=f"manage_referrals_{user_id}")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')

async def handle_full_report_action(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """تقرير شامل للمستخدم"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.data.split("_")[-1]
    user_data = context.user_data.get('selected_user_data')
    
    if not user_data:
        await query.edit_message_text("❌ خطأ: بيانات المستخدم غير متوفرة")
        return
    
    # الحصول على بيانات شاملة
    current_balance = float(user_data[6]) if user_data[6] else 0.0
    referral_earned = float(user_data[5]) if user_data[5] else 0.0
    
    # إحصائيات الطلبات
    orders_stats = db.execute_query("""
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed,
            SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending,
            SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed,
            SUM(CASE WHEN status = 'completed' THEN payment_amount ELSE 0 END) as total_spent
        FROM orders WHERE user_id = ?
    """, (user_id,))
    
    stats = orders_stats[0] if orders_stats else (0, 0, 0, 0, 0)
    total_spent = float(stats[4]) if stats[4] is not None else 0.0
    
    # إحصائيات الإحالات
    referral_count = db.execute_query("SELECT COUNT(*) FROM referrals WHERE referrer_id = ?", (user_id,))[0][0]
    
    # آخر نشاط
    last_order = db.execute_query("SELECT created_at FROM orders WHERE user_id = ? ORDER BY created_at DESC LIMIT 1", (user_id,))
    last_activity = last_order[0][0][:10] if last_order else "لا يوجد"
    
    report = f"""📊 **التقرير الشامل**

👤 **المستخدم:** {user_data[2]} {user_data[3]}
🆔 **المعرف:** `{user_id}`
📅 **تاريخ الانضمام:** {user_data[7][:10] if user_data[7] else 'غير معروف'}

━━━━━━━━━━━━━━━━━━━━━━━
💰 **الملف المالي**
• الرصيد الحالي: `${current_balance:.2f}`
• رصيد الإحالات: `${referral_earned:.2f}`
• إجمالي الإنفاق: `${total_spent:.2f}`
• صافي الرصيد: `${(current_balance + referral_earned):.2f}`

━━━━━━━━━━━━━━━━━━━━━━━
📈 **إحصائيات الطلبات**
• إجمالي الطلبات: `{stats[0]}`
• المكتملة: `{stats[1]}`
• المعلقة: `{stats[2]}`
• الفاشلة: `{stats[3]}`

━━━━━━━━━━━━━━━━━━━━━━━
👥 **نظام الإحالات**
• عدد المُحالين: `{referral_count}`
• أرباح الإحالات: `${referral_earned:.2f}`

━━━━━━━━━━━━━━━━━━━━━━━
📅 **النشاط**
• آخر طلب: {last_activity}"""
    
    keyboard = [[InlineKeyboardButton("🔙 رجوع للتقارير", callback_data=f"detailed_reports_{user_id}")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(report, reply_markup=reply_markup, parse_mode='Markdown')

async def handle_financial_report_action(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """التقرير المالي المفصل"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.data.split("_")[-1]
    user_data = context.user_data.get('selected_user_data')
    
    if not user_data:
        await query.edit_message_text("❌ خطأ: بيانات المستخدم غير متوفرة")
        return
    
    current_balance = float(user_data[6]) if user_data[6] else 0.0
    referral_earned = float(user_data[5]) if user_data[5] else 0.0
    
    # الحصول على تفاصيل المعاملات المالية
    transactions = db.execute_query("""
        SELECT transaction_type, amount, created_at, description
        FROM credits_transactions 
        WHERE user_id = ? 
        ORDER BY created_at DESC LIMIT 10
    """, (user_id,))
    
    # حساب الإنفاق حسب نوع الخدمة
    spending_by_service = db.execute_query("""
        SELECT proxy_type, COUNT(*), SUM(payment_amount)
        FROM orders 
        WHERE user_id = ? AND status = 'completed'
        GROUP BY proxy_type
    """, (user_id,))
    
    report = f"""💰 **التقرير المالي المفصل**

👤 **المستخدم:** {user_data[2]} {user_data[3]}

━━━━━━━━━━━━━━━━━━━━━━━
💳 **الرصيد الحالي**
• الرصيد الأساسي: `${current_balance:.2f}`
• رصيد الإحالات: `${referral_earned:.2f}`
• المجموع: `${(current_balance + referral_earned):.2f}`

━━━━━━━━━━━━━━━━━━━━━━━
📊 **الإنفاق حسب الخدمة**"""
    
    if spending_by_service:
        for service, count, total in spending_by_service:
            total_amount = float(total) if total is not None else 0.0
            report += f"\n• **{service}**: {count} طلب → `${total_amount:.2f}`"
    else:
        report += "\n• لا توجد مشتريات مكتملة"
    
    if transactions:
        report += f"\n\n━━━━━━━━━━━━━━━━━━━━━━━\n📝 **آخر المعاملات**"
        for trans_type, amount, created_at, desc in transactions[:5]:
            date = created_at[:10] if created_at else "غير معروف"
            sign = "+" if amount > 0 else ""
            report += f"\n• **{sign}${amount:.2f}** - {date}\n  {desc or trans_type}"
    
    keyboard = [[InlineKeyboardButton("🔙 رجوع للتقارير", callback_data=f"detailed_reports_{user_id}")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(report, reply_markup=reply_markup, parse_mode='Markdown')

async def handle_orders_report_action(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """تقرير الطلبات المفصل"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.data.split("_")[-1]
    
    # الحصول على تفاصيل الطلبات
    orders = db.execute_query("""
        SELECT id, proxy_type, country, state, status, payment_amount, created_at
        FROM orders 
        WHERE user_id = ? 
        ORDER BY created_at DESC LIMIT 10
    """, (user_id,))
    
    report = f"📦 **تقرير الطلبات المفصل**\n\n🆔 **المعرف:** `{user_id}`\n\n━━━━━━━━━━━━━━━━━━━━━━━"
    
    if not orders:
        report += "\n\n❌ لا توجد طلبات مسجلة"
    else:
        # إحصائيات سريعة
        completed = sum(1 for o in orders if o[4] == 'completed')
        pending = sum(1 for o in orders if o[4] == 'pending') 
        failed = sum(1 for o in orders if o[4] == 'failed')
        
        report += f"\n\n📊 **الملخص:**\n• المكتملة: {completed}\n• المعلقة: {pending}\n• الفاشلة: {failed}\n\n📋 **آخر الطلبات:**"
        
        for i, (order_id, proxy_type, country, state, status, amount, created_at) in enumerate(orders[:5], 1):
            status_emoji = {"completed": "✅", "pending": "⏳", "failed": "❌"}.get(status, "❓")
            location = f"{country}-{state}" if state else country
            date = created_at[:10] if created_at else "غير معروف"
            order_amount = float(amount) if amount is not None else 0.0
            
            report += f"\n\n**{i}.** {status_emoji} **{proxy_type}**"
            report += f"\n   • الموقع: {location}"
            report += f"\n   • المبلغ: ${order_amount:.2f}"
            report += f"\n   • التاريخ: {date}"
            report += f"\n   • المعرف: `{order_id[:8]}...`"
    
    keyboard = [[InlineKeyboardButton("🔙 رجوع للتقارير", callback_data=f"detailed_reports_{user_id}")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(report, reply_markup=reply_markup, parse_mode='Markdown')

async def handle_referrals_report_action(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """تقرير الإحالات المفصل"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.data.split("_")[-1]
    user_data = context.user_data.get('selected_user_data')
    
    if not user_data:
        await query.edit_message_text("❌ خطأ: بيانات المستخدم غير متوفرة")
        return
    
    # الحصول على تفاصيل الإحالات
    referrals = db.execute_query("""
        SELECT u.user_id, u.first_name, u.last_name, u.username, r.created_at,
               (SELECT COUNT(*) FROM orders WHERE user_id = u.user_id AND status = 'completed') as orders_count
        FROM referrals r
        JOIN users u ON r.referred_id = u.user_id
        WHERE r.referrer_id = ?
        ORDER BY r.created_at DESC
    """, (user_id,))
    
    referral_earnings = float(user_data[5]) if user_data[5] else 0.0
    
    report = f"👥 **تقرير الإحالات المفصل**\n\n📋 **المستخدم:** {user_data[2]} {user_data[3]}\n🆔 **المعرف:** `{user_id}`"
    report += f"\n\n💰 **إجمالي الأرباح:** `${referral_earnings:.2f}`"
    report += f"\n👥 **عدد المُحالين:** {len(referrals)}"
    
    if not referrals:
        report += "\n\n❌ لا يوجد مستخدمون محالون"
    else:
        report += f"\n\n━━━━━━━━━━━━━━━━━━━━━━━\n📊 **تفاصيل المُحالين:**"
        
        # إحصائيات الإحالات النشطة
        active_referrals = [r for r in referrals if r[5] > 0]  # لديهم طلبات
        report += f"\n• النشطون: {len(active_referrals)} من أصل {len(referrals)}"
        
        for i, (ref_id, fname, lname, username, created_at, orders_count) in enumerate(referrals[:8], 1):
            name = f"{fname} {lname}".strip()
            username_text = f"@{username}" if username else "لا يوجد"
            date = created_at[:10] if created_at else "غير معروف"
            activity = "🟢 نشط" if orders_count > 0 else "🟡 غير نشط"
            
            report += f"\n\n**{i}.** {name} ({username_text})"
            report += f"\n   • المعرف: `{ref_id}`"
            report += f"\n   • الطلبات: {orders_count}"
            report += f"\n   • تاريخ الإحالة: {date}"
            report += f"\n   • الحالة: {activity}"
        
        if len(referrals) > 8:
            report += f"\n\n📋 *عرض أول 8 من أصل {len(referrals)} محال*"
    
    keyboard = [[InlineKeyboardButton("🔙 رجوع للتقارير", callback_data=f"detailed_reports_{user_id}")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(report, reply_markup=reply_markup, parse_mode='Markdown')

async def handle_advanced_stats_action(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """الإحصائيات المتقدمة"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.data.split("_")[-1]
    user_data = context.user_data.get('selected_user_data')
    
    if not user_data:
        await query.edit_message_text("❌ خطأ: بيانات المستخدم غير متوفرة")
        return
    
    # إحصائيات متقدمة
    join_date = user_data[7][:10] if user_data[7] else "غير معروف"
    days_since_join = (datetime.now() - datetime.fromisoformat(user_data[7])).days if user_data[7] else 0
    
    # إحصائيات الطلبات بالتفصيل
    monthly_stats = db.execute_query("""
        SELECT 
            strftime('%Y-%m', created_at) as month,
            COUNT(*) as orders,
            SUM(payment_amount) as spent
        FROM orders 
        WHERE user_id = ? AND status = 'completed'
        GROUP BY strftime('%Y-%m', created_at)
        ORDER BY month DESC LIMIT 6
    """, (user_id,))
    
    # معدل الإنفاق
    total_orders = db.execute_query("SELECT COUNT(*) FROM orders WHERE user_id = ? AND status = 'completed'", (user_id,))[0][0]
    total_spent = db.execute_query("SELECT COALESCE(SUM(payment_amount), 0) FROM orders WHERE user_id = ? AND status = 'completed'", (user_id,))[0][0]
    avg_order_value = float(total_spent) / total_orders if total_orders > 0 else 0
    
    report = f"""📈 **الإحصائيات المتقدمة**

👤 **المستخدم:** {user_data[2]} {user_data[3]}
📅 **تاريخ الانضمام:** {join_date}
⏳ **مدة العضوية:** {days_since_join} يوم

━━━━━━━━━━━━━━━━━━━━━━━
📊 **التحليل المالي**
• إجمالي الطلبات: {total_orders}
• إجمالي الإنفاق: `${float(total_spent):.2f}`
• متوسط قيمة الطلب: `${avg_order_value:.2f}`
• معدل الإنفاق اليومي: `${(float(total_spent) / max(days_since_join, 1)):.2f}`"""
    
    if monthly_stats:
        report += f"\n\n━━━━━━━━━━━━━━━━━━━━━━━\n📅 **الإحصائيات الشهرية**"
        for month, orders, spent in monthly_stats:
            spent_amount = float(spent) if spent is not None else 0.0
            report += f"\n• **{month}**: {orders} طلب → `${spent_amount:.2f}`"
    
    # إحصائيات الإحالات
    referral_count = db.execute_query("SELECT COUNT(*) FROM referrals WHERE referrer_id = ?", (user_id,))[0][0]
    referral_conversion = (referral_count / max(days_since_join, 1)) * 30 if days_since_join > 0 else 0
    
    report += f"\n\n━━━━━━━━━━━━━━━━━━━━━━━\n👥 **تحليل الإحالات**"
    report += f"\n• عدد المُحالين: {referral_count}"
    report += f"\n• معدل الإحالة الشهري: {referral_conversion:.1f}"
    
    keyboard = [[InlineKeyboardButton("🔙 رجوع للتقارير", callback_data=f"detailed_reports_{user_id}")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(report, reply_markup=reply_markup, parse_mode='Markdown')

async def handle_timeline_report_action(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """التقرير الزمني"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.data.split("_")[-1]
    user_data = context.user_data.get('selected_user_data')
    
    if not user_data:
        await query.edit_message_text("❌ خطأ: بيانات المستخدم غير متوفرة")
        return
    
    # الحصول على التسلسل الزمني للأنشطة
    timeline_events = []
    
    # تاريخ الانضمام
    join_date = user_data[7]
    if join_date:
        timeline_events.append((join_date, "🎯 انضمام للبوت", "تسجيل حساب جديد"))
    
    # الطلبات الهامة
    important_orders = db.execute_query("""
        SELECT created_at, proxy_type, status, payment_amount
        FROM orders 
        WHERE user_id = ? 
        ORDER BY created_at DESC LIMIT 20
    """, (user_id,))
    
    for order_date, proxy_type, status, amount in important_orders:
        order_amount = float(amount) if amount is not None else 0.0
        if status == 'completed':
            timeline_events.append((order_date, f"✅ طلب مكتمل", f"{proxy_type} - ${order_amount:.2f}"))
        elif status == 'failed':
            timeline_events.append((order_date, f"❌ طلب فاشل", f"{proxy_type} - ${order_amount:.2f}"))
    
    # أول إحالة
    first_referral = db.execute_query("""
        SELECT r.created_at, u.first_name, u.last_name
        FROM referrals r
        JOIN users u ON r.referred_id = u.user_id
        WHERE r.referrer_id = ?
        ORDER BY r.created_at ASC LIMIT 1
    """, (user_id,))
    
    if first_referral:
        ref_date, fname, lname = first_referral[0]
        timeline_events.append((ref_date, "👥 أول إحالة", f"أحال {fname} {lname}"))
    
    # ترتيب الأحداث حسب التاريخ
    timeline_events.sort(key=lambda x: x[0] if x[0] else "", reverse=True)
    
    report = f"""📅 **التقرير الزمني**

👤 **المستخدم:** {user_data[2]} {user_data[3]}
🆔 **المعرف:** `{user_id}`

━━━━━━━━━━━━━━━━━━━━━━━
⏳ **التسلسل الزمني للأنشطة**"""
    
    if not timeline_events:
        report += "\n\n❌ لا توجد أنشطة مسجلة"
    else:
        for i, (event_date, event_type, description) in enumerate(timeline_events[:15], 1):
            date = event_date[:10] if event_date else "غير معروف"
            report += f"\n\n**{i}.** {event_type}"
            report += f"\n   📅 {date}"
            report += f"\n   📝 {description}"
        
        if len(timeline_events) > 15:
            report += f"\n\n📋 *عرض أول 15 حدث من أصل {len(timeline_events)}*"
    
    keyboard = [[InlineKeyboardButton("🔙 رجوع للتقارير", callback_data=f"detailed_reports_{user_id}")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(report, reply_markup=reply_markup, parse_mode='Markdown')

async def handle_transaction_history_action(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """سجل المعاملات المالية"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.data.split("_")[-1]
    
    # الحصول على سجل المعاملات
    transactions = db.execute_query("""
        SELECT transaction_type, amount, created_at, description, order_id
        FROM credits_transactions 
        WHERE user_id = ? 
        ORDER BY created_at DESC LIMIT 15
    """, (user_id,))
    
    report = f"💳 سجل المعاملات المالية\n\n🆔 المعرف: {user_id}"
    
    if not transactions:
        report += "\n\n❌ لا توجد معاملات مسجلة"
    else:
        # حساب الرصيد
        total_credit = sum(float(t[1]) for t in transactions if t[1] is not None and float(t[1]) > 0)
        total_debit = sum(abs(float(t[1])) for t in transactions if t[1] is not None and float(t[1]) < 0)
        
        report += f"\n\n📊 ملخص المعاملات:"
        report += f"\n• إجمالي الإيداعات: +${total_credit:.2f}"
        report += f"\n• إجمالي المسحوبات: -${total_debit:.2f}"
        report += f"\n• صافي المعاملات: ${(total_credit - total_debit):.2f}"
        
        report += f"\n\n━━━━━━━━━━━━━━━━━━━━━━━\n📝 تفاصيل المعاملات:"
        
        for i, (trans_type, amount, created_at, desc, order_id) in enumerate(transactions, 1):
            date = created_at[:10] if created_at else "غير معروف"
            amount_float = float(amount) if amount is not None else 0.0
            sign = "+" if amount_float > 0 else "-"
            color = "🟢" if amount_float > 0 else "🔴"
            
            report += f"\n\n{i}. {color} {sign}${abs(amount_float):.2f}"
            report += f"\n   📅 {date}"
            report += f"\n   📝 {desc or trans_type}"
            if order_id:
                report += f"\n   🔗 الطلب: {order_id[:8]}..."
    
    keyboard = [[InlineKeyboardButton("🔙 رجوع لإدارة النقاط", callback_data=f"manage_points_{user_id}")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(report, reply_markup=reply_markup)

async def handle_custom_balance_action(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """تعديل الرصيد لقيمة مخصصة"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.data.split("_")[-1]
    user_data = context.user_data.get('selected_user_data')
    
    if not user_data:
        await query.edit_message_text("❌ خطأ: بيانات المستخدم غير متوفرة")
        return
    
    current_balance = float(user_data[6]) if user_data[6] else 0.0
    
    message = f"""💰 تعديل الرصيد المخصص

📋 المستخدم: {user_data[2]} {user_data[3]}
💳 الرصيد الحالي: ${current_balance:.2f}

⚠️ تحذير هام:
هذه العملية ستغير الرصيد إلى القيمة المحددة تماماً
(وليس إضافة أو خصم)

📝 أرسل الرصيد الجديد بالدولار:
مثال: 50.00 أو 25.5 أو 100"""
    
    # حفظ بيانات التعديل المخصص
    context.user_data['custom_balance_user_id'] = user_id
    context.user_data['awaiting_custom_balance'] = True
    
    keyboard = [[InlineKeyboardButton("❌ إلغاء", callback_data=f"manage_points_{user_id}")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')

async def handle_custom_balance_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالجة إدخال الرصيد المخصص"""
    if not context.user_data.get('awaiting_custom_balance'):
        return
    
    user_id = context.user_data.get('custom_balance_user_id')
    if not user_id:
        await update.message.reply_text("❌ خطأ: معرف المستخدم غير موجود")
        context.user_data.pop('awaiting_custom_balance', None)
        return
    
    balance_text = update.message.text.strip()
    
    # التحقق من أن القيمة رقم عشري صحيح
    try:
        new_balance = float(balance_text)
        if new_balance < 0:
            await update.message.reply_text(
                "❌ الرصيد لا يمكن أن يكون سالباً!\n\n📝 أرسل رصيد صحيح (مثال: 50.00 أو 25.5)"
            )
            return
    except ValueError:
        await update.message.reply_text(
            "❌ قيمة غير صحيحة!\n\n📝 أرسل رقم عشري صحيح (مثال: 50.00 أو 25.5 أو 100)"
        )
        return
    
    # الحصول على بيانات المستخدم
    user_result = db.execute_query("SELECT * FROM users WHERE user_id = ?", (user_id,))
    if not user_result:
        await update.message.reply_text("❌ المستخدم غير موجود")
        context.user_data.pop('awaiting_custom_balance', None)
        return
    
    user_data = user_result[0]
    old_balance = float(user_data[6]) if user_data[6] else 0.0
    
    # تعديل الرصيد
    db.execute_query("UPDATE users SET credits_balance = ? WHERE user_id = ?", (new_balance, user_id))
    
    # تسجيل المعاملة
    difference = new_balance - old_balance
    transaction_type = "manual_credit" if difference >= 0 else "manual_debit"
    description = f"تعديل يدوي للرصيد بواسطة الأدمن (من ${old_balance:.2f} إلى ${new_balance:.2f})"
    
    db.execute_query("""
        INSERT INTO credits_transactions (user_id, transaction_type, amount, description, created_at)
        VALUES (?, ?, ?, ?, datetime('now'))
    """, (user_id, transaction_type, difference, description))
    
    success_message = f"""✅ تم تعديل الرصيد بنجاح!

📋 المستخدم: {user_data[2]} {user_data[3]}
🆔 المعرف: `{user_id}`

💰 الرصيد السابق: ${old_balance:.2f}
💰 الرصيد الجديد: ${new_balance:.2f}
📊 الفرق: {"+" if difference >= 0 else ""}{difference:.2f}"""
    
    await update.message.reply_text(success_message, parse_mode='Markdown')
    
    # إعادة تفعيل كيبورد الأدمن
    await restore_admin_keyboard(context, update.effective_chat.id, "✅ تم التعديل - لوحة الأدمن جاهزة")
    
    # تنظيف البيانات
    context.user_data.pop('awaiting_custom_balance', None)
    context.user_data.pop('custom_balance_user_id', None)

async def handle_reset_stats_action(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """إعادة تعيين الإحصائيات"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.data.split("_")[-1]
    user_data = context.user_data.get('selected_user_data')
    
    if not user_data:
        await query.edit_message_text("❌ خطأ: بيانات المستخدم غير متوفرة")
        return
    
    message = f"""📊 **إعادة تعيين الإحصائيات**

📋 **المستخدم:** {user_data[2]} {user_data[3]}
🆔 **المعرف:** `{user_id}`

⚠️ **تحذير خطر:**
هذه العملية ستحذف نهائياً:
• جميع الطلبات والتاريخ
• سجل المعاملات المالية  
• إحصائيات الاستخدام
• لن يتم حذف الرصيد أو الإحالات

❌ **هذه العملية لا يمكن التراجع عنها!**

هل أنت متأكد من المتابعة؟"""
    
    keyboard = [
        [
            InlineKeyboardButton("✅ نعم، إعادة تعيين الإحصائيات", callback_data=f"confirm_reset_stats_{user_id}"),
            InlineKeyboardButton("❌ إلغاء", callback_data=f"manage_user_{user_id}")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')

async def handle_delete_user_data_action(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """حذف بيانات المستخدم"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.data.split("_")[-1]
    user_data = context.user_data.get('selected_user_data')
    
    if not user_data:
        await query.edit_message_text("❌ خطأ: بيانات المستخدم غير متوفرة")
        return
    
    message = f"""🗑️ **حذف بيانات المستخدم**

📋 **المستخدم:** {user_data[2]} {user_data[3]}
🆔 **المعرف:** `{user_id}`

💀 **تحذير خطر شديد:**
هذه العملية ستحذف نهائياً:
• ملف المستخدم بالكامل
• جميع الطلبات والتاريخ  
• الرصيد والنقاط
• الإحالات وأرباحها
• سجل المعاملات المالية
• جميع البيانات المرتبطة

❌ **هذه العملية لا يمكن التراجع عنها إطلاقاً!**
⚠️ **استخدم هذا فقط في الحالات القصوى!**

هل أنت متأكد 100% من الحذف النهائي؟"""
    
    keyboard = [
        [InlineKeyboardButton("💀 نعم، حذف نهائي للمستخدم", callback_data=f"confirm_delete_user_{user_id}")],
        [InlineKeyboardButton("❌ إلغاء (الخيار الآمن)", callback_data=f"manage_user_{user_id}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')

async def handle_clear_referrals_action(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """مسح جميع الإحالات"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.data.split("_")[-1]
    user_data = context.user_data.get('selected_user_data')
    
    if not user_data:
        await query.edit_message_text("❌ خطأ: بيانات المستخدم غير متوفرة")
        return
    
    # الحصول على عدد الإحالات
    referral_count = db.execute_query("SELECT COUNT(*) FROM referrals WHERE referrer_id = ?", (user_id,))[0][0]
    referral_earned = float(user_data[5]) if user_data[5] else 0.0
    
    message = f"""🔄 **مسح جميع الإحالات**

📋 **المستخدم:** {user_data[2]} {user_data[3]}
🆔 **المعرف:** `{user_id}`

📊 **البيانات الحالية:**
• عدد المُحالين: `{referral_count}` شخص
• رصيد الإحالات: `${referral_earned:.2f}`

⚠️ **تحذير:**
هذه العملية ستحذف:
• جميع سجلات الإحالات ({referral_count} إحالة)
• سيتم تصفير رصيد الإحالات
• لن يتأثر الرصيد الأساسي للمستخدم

❌ **لا يمكن التراجع عن هذه العملية!**

هل تريد المتابعة؟"""
    
    keyboard = [
        [
            InlineKeyboardButton("🗑️ نعم، مسح جميع الإحالات", callback_data=f"confirm_clear_referrals_{user_id}"),
            InlineKeyboardButton("❌ إلغاء", callback_data=f"manage_referrals_{user_id}")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')

async def handle_static_services_report(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالجة تقارير الخدمات الستاتيك"""
    query = update.callback_query
    await query.answer()
    
    # الحصول على إحصائيات شاملة
    report_data = db.get_comprehensive_service_report()
    
    keyboard = []
    keyboard.append([InlineKeyboardButton("🔄 تحديث التقرير", callback_data="static_services_report")])
    keyboard.append([InlineKeyboardButton("📥 تصدير التقرير", callback_data="export_services_report")])
    keyboard.append([InlineKeyboardButton("🔙 رجوع", callback_data="manage_static_services")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    report_text = f"""📊 **تقرير خدمات الستاتيك الشامل**
━━━━━━━━━━━━━━━━━━━━━━━

📈 **إجمالي الطلبات:** {report_data.get('total_orders', 0)}
💰 **إجمالي الإيرادات:** ${report_data.get('total_revenue', 0)}
👥 **عدد العملاء النشطين:** {report_data.get('active_users', 0)}

🏢 **ريزيدنتال:** {report_data.get('residential_orders', 0)} طلب
🏠 **Residential Crocker:** {report_data.get('verizon_orders', 0)} طلب  
📅 **أسبوعي Crocker:** {report_data.get('weekly_orders', 0)} طلب
🌐 **ISP:** {report_data.get('isp_orders', 0)} طلب

📅 **آخر تحديث:** {datetime.now().strftime('%Y-%m-%d %H:%M')}
"""
    
    await query.edit_message_text(
        report_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

def main():
    """الدالة الرئيسية لتشغيل البوت"""
    lock_file = None
    try:
        print("=" * 50)
        print("🤖 تشغيل بوت البروكسي")
        print("=" * 50)
        
        # فحص وإنشاء قفل البوت
        lock_file = check_bot_lock()
        if lock_file is None and FCNTL_AVAILABLE:
            # في أنظمة Unix، إذا فشل القفل فلا نكمل
            return
            
        # تسجيل دالة تنظيف عند إغلاق البرنامج
        def cleanup_lock():
            cleanup_bot_lock(lock_file)
        
        atexit.register(cleanup_lock)
        
        # إعداد البوت
        application = setup_bot()
        if application is None:
            print("❌ فشل في إعداد البوت")
            return
        
        # تشغيل البوت
        print("🚀 بدء تشغيل البوت...")
        application.run_polling(
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=True
        )
        
    except KeyboardInterrupt:
        print("\n⚠️ تم إيقاف البوت بواسطة المستخدم")
    except Exception as e:
        print(f"❌ خطأ فادح في البوت: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # تنظيف ملف القفل
        cleanup_bot_lock(lock_file)
        print("✅ تم إيقاف البوت بنجاح")

if __name__ == '__main__':
    main()


