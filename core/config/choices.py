from django.db import models


class Gender(models.TextChoices):
    MALE = "M", "Male"
    FEMALE = "F", "Female"
    OTHERS = "O", "Others"


class Title(models.TextChoices):
    MR = "Mr", "Mr"
    MRS = "Mrs", "Mrs"
    MISS = "Miss", "Miss"


class MaritalStatus(models.TextChoices):
    SINGLE = "single", "Single"
    MARRIED = "married", "Married"
    DIVORCED = "divorced", "Divorced"
    WIDOWED = "widowed", "Widowed"


class UserStatus(models.TextChoices):
    NONE = "none", "None"
    BRONZE = "bronze", "Bronze"
    SILVER = "silver", "Silver"
    GOLD = "gold", "Gold"
    PLATINUM = "platinum", "Platinum"


class UserType(models.TextChoices):
    SHOP_OWNER = "shop owner", "Shop owner"
    CUSTOMER = "customer", "Customer"
    ARCHIVED = "archived", "Archived"
    ADMIN = "admin", "Admin"


class BusinessRating(models.TextChoices):
    LEVEL_1 = "level 1", "Level 1"
    LEVEL_2 = "level 2", "Level 2"
    LEVEL_3 = "level 3", "Level 3"
    LEVEL_4 = "level 4", "Level 4"
    LEVEL_5 = "level 5", "Level 5"


class ProductCategory(models.TextChoices):
    RANDOM = "random", "Random"
    FASHION = "fashion", "Fashion"
    ELECTRONICS = "electronics", "Electronics"
    FURNITURE = "furniture", "Furniture"
    GROCERY = "grocery", "Grocery"
    COMPUTERS = "computers", "Computers"
    BOOKS = "books and literature", "Books & Literature"


class DiscountType(models.TextChoices):
    CURRENCY = "currency", "Currency"
    PERCENTAGE = "percentage", "Percentage"
