from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str
    GEMINI_API_KEY: str
    #SOILGRIDS_API_KEY: str
    #OPENWEATHER_API_KEY: str
    #TWILIO_ACCOUNT_SID: str
    #TWILIO_AUTH_TOKEN: str
    #TWILIO_PHONE_NUMBER: str

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings(GEMINI_API_KEY="AIzaSyDBxs1alLA5dJK6n2B6rXHuPoIgfuq0PLk",DATABASE_URL="sqlite:///./sql_app.db")