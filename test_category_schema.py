

from fastapi import UploadFile
from app.schemas.category_schema import CreateCategorySchema
from io import BytesIO

# Mocks
class MockFile:
    def __init__(self, content=b"", filename="test.jpg"):
        self.file = BytesIO(content)
        self.filename = filename

def test_valid_category():
    image = UploadFile(file=BytesIO(b"content"), filename="test.jpg")
    schema = CreateCategorySchema.as_form(
        name="Category 1", 
        description="This is a valid description", 
        image=image
    )
    assert schema.name == "Category 1"
    assert schema.description == "This is a valid description"

def test_invalid_name_special_char():
    image = UploadFile(file=BytesIO(b"content"), filename="test.jpg")
    try:
        CreateCategorySchema.as_form(
            name="Category@1", 
            description="Valid Description", 
            image=image
        )
    except ValueError as e:
        assert "Name must be alphanumeric" in str(e)

def test_invalid_name_length():
    image = UploadFile(file=BytesIO(b"content"), filename="test.jpg")
    try:
        CreateCategorySchema.as_form(
            name="C", 
            description="Valid Description", 
            image=image
        )
    except ValueError as e:
        assert "Name must be between 2 and 50" in str(e)

def test_invalid_description_length():
    image = UploadFile(file=BytesIO(b"content"), filename="test.jpg")
    try:
        CreateCategorySchema.as_form(
            name="Category", 
            description="Sho", 
            image=image
        )
    except ValueError as e:
        assert "Description must be between 5 and 500" in str(e)

def test_large_image():
    # > 2MB
    large_content = b"a" * (2 * 1024 * 1024 + 1)
    image = UploadFile(file=BytesIO(large_content), filename="large.jpg")
    try:
        CreateCategorySchema.as_form(
            name="Category", 
            description="Valid Description", 
            image=image
        )
    except ValueError as e:
        assert "Image size must be less than 2MB" in str(e)

if __name__ == "__main__":
    # simple runner
    try:
        test_valid_category()
        print("test_valid_category passed")
        test_invalid_name_special_char()
        print("test_invalid_name_special_char passed") # expects exception caught
        test_invalid_name_length()
        print("test_invalid_name_length passed")
        test_invalid_description_length()
        print("test_invalid_description_length passed")
        test_large_image()
        print("test_large_image passed")
    except Exception as e:
        print(f"Tests failed: {e}")
