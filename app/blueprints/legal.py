from flask import Blueprint, render_template

legal = Blueprint('legal', __name__)

@legal.route('/privacy')
def privacy():
    return render_template('legal/privacy.html')

@legal.route('/terms')
def terms():
    return render_template('legal/terms.html')

@legal.route('/cookies')
def cookies():
    return render_template('legal/cookies.html')

@legal.route('/legal-notice')
def legal_notice():
    return render_template('legal/legal_notice.html')

@legal.route('/disclaimer')
def disclaimer():
    return render_template('legal/disclaimer.html')

@legal.route('/eula')
def eula():
    return render_template('legal/eula.html')

@legal.route('/faq')
def faq():
    return render_template('legal/faq.html')

@legal.route('/aup')
def aup():
    return render_template('legal/aup.html')

@legal.route('/about')
def about():
    return render_template('legal/about.html')
