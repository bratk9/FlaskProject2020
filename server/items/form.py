from flask_wtf import FlaskForm
from flask_wtf.file import FileField,FileAllowed
from wtforms import StringField,SubmitField
from wtforms.fields import FloatField
from wtforms.validators import DataRequired,length

class addItemForm(FlaskForm):
    Item_Name=StringField("Item Name",validators=[DataRequired(),length(min=2)])
    Price=FloatField("Price",validators=[DataRequired()])
    Picture=FileField("Image of Item",validators=[FileAllowed(["png","jpg"]),DataRequired()])
    Submit=SubmitField("Add Product")
