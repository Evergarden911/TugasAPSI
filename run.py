from app.main import create_app

# Menginstansiasi aplikasi dari pabrik
app = create_app()

if __name__ == '__main__':
    # Titik eksekusi khusus untuk peladen pengembangan lokal
    app.run(debug=True, host='0.0.0.0', port=5000)