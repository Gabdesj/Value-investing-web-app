from flask import Flask, render_template, request  # type: ignore
import yfinance as yf # type: ignore
from waitress import serve # type: ignore

app = Flask(__name__)

@app.route('/')
def index():
    ticker_symbol = request.args.get('ticker', 'AAPL').upper()
    stock = yf.Ticker(ticker_symbol)
    
    # Ratios
    info = stock.info
    pe_ratio = info.get('trailingPE', 'N/A')
    pb_ratio = info.get('priceToBook', 'N/A')
    
    # Récupération du Free Cash Flow
    try:
        # On récupère le tableau des flux de trésorerie trimestriels
        df_cf = stock.quarterly_cashflow
        
        # Extraction de la ligne 'Free Cash Flow'
        # On prend les 4 colonnes les plus récentes
        if 'Free Cash Flow' in df_cf.index:
            fcf_data = df_cf.loc['Free Cash Flow'].iloc[:4].to_dict()
        else:
            # Calcul manuel si la ligne n'existe pas : Op. Cash Flow - CapEx
            fcf_data = (df_cf.loc['Operating Cash Flow'] + df_cf.loc['Capital Expenditure']).iloc[:4].to_dict()
            
    except Exception as e:
        fcf_data = {"Erreur": "Données FCF non disponibles"}

    return render_template('index.html', 
                           ticker=ticker_symbol,
                           pe=pe_ratio, 
                           pb=pb_ratio, 
                           cash_flow=fcf_data)


if __name__ == '__main__':
    print("Serveur de production Waitress lancé sur http://0.0.0.0:8080")
    # host='0.0.0.0' permet au serveur d'être accessible sur votre réseau local
    # threads=4 (par défaut) permet de gérer plusieurs requêtes en même temps
    serve(app, host='0.0.0.0', port=8080)