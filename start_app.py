# -*- coding: utf-8 -*-
import uvicorn
from app.main import app

if __name__ == "__main__":
    # Porta e host mantidos como na versão antiga
    uvicorn.run(app, host="127.0.0.1", port=8011, log_level="info")
