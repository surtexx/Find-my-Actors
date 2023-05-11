from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
from flask import current_app

views =  Blueprint( 'views' ,  __name__ )

@views.route( '/' )
def  home():
    return  render_template( "home.html", user=current_user)


        