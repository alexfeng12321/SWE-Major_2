from flask import Flask, render_template, request, redirect, url_for, session
import userManagement as dbHandler
import pyotp
import pyqrcode
import os
import base64
from io import BytesIO

