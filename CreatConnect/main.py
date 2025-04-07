'''
main.py - Entry point for CreatConnect App
''' 
# installing kivy packages/dependencies: pip install kivy kivy-ios matplotlib pandas requests

from kivy.app import App
from user_interface import CreatConnectUI 


class CreatConnectApp(App):
    def build(self):
        return CreatConnectUI()
    
if __name__ == "__main__":
    CreatConnectApp().run()