from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.button import MDFlatButton

KV = '''
MDScreen: 

    MDBoxLayout:
        adaptive_size: True
    
    MDTopAppBar:
        title: 'НФ УУНиТ'
        type_height: "small"
        theme_font_styles: 'Title medium'
        pos_hint: {"top": 1}
        md_bg_color: 0, 0, 100, 100
        right_action_items: [["dots-vertical", lambda x: x]]
        left_action_items: [["menu", lambda x: nav_drawer]]
        
         
    MDNavigationDrawer:
        id: nav_drawer
        drawer_type: "modal"
        anchor: "left"
        
        MDNavigationDrawerItem:
            

'''

class Example(MDApp):
    '''
    def on_start(self):
        self.fps_monitor_start()
    '''
    def build(self):
        self.theme_cls.theme_style_switch_animation = True
        self.theme_cls.theme_style = "Dark"
        return Builder.load_string(KV)

    def switch_theme_style(self):
        self.theme_cls.theme_style = (
            "Dark" if self.theme_cls.theme_style == "Light" else "Light"
        )

Example().run()