"""
就诊数据采集系统 - 测试版本
包含详细的异常处理和状态提示
"""

import sys
import traceback

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window
from kivy.core.text import LabelBase
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.clock import Clock
from kivy.logger import Logger

# 字体配置
font_loaded = False
try:
    # 尝试加载微软雅黑字体
    LabelBase.register(name='ChineseFont', fn_regular='C:/Windows/Fonts/msyh.ttc')
    font_loaded = True
    print("成功加载中文字体: 微软雅黑")
except Exception as e:
    print(f"加载微软雅黑字体失败: {e}")
    try:
        # 尝试备用字体
        LabelBase.register(name='ChineseFont', fn_regular='/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc')
        font_loaded = True
        print("成功加载中文字体: 文泉驿正黑")
    except Exception as e2:
        print(f"加载备用字体失败: {e2}")
        print("将使用系统默认字体，中文可能显示为方框")

FONT_NAME = 'ChineseFont' if font_loaded else 'Roboto'
print(f"使用字体: {FONT_NAME}")

# 自定义支持中文的Label类
class CLabel(Label):
    """支持中文的Label"""
    def __init__(self, **kwargs):
        kwargs['font_name'] = FONT_NAME
        super().__init__(**kwargs)

# 自定义支持中文的Button类
class CButton(Button):
    """支持中文的Button"""
    def __init__(self, **kwargs):
        kwargs['font_name'] = FONT_NAME
        super().__init__(**kwargs)

# 自定义支持中文的TextInput类
class CTextInput(TextInput):
    """支持中文的TextInput"""
    def __init__(self, **kwargs):
        kwargs['font_name'] = FONT_NAME
        super().__init__(**kwargs)

# 设置窗口大小（模拟手机屏幕）
Window.size = (360, 640)
Window.clearcolor = (0.95, 0.95, 0.95, 1)

# 全局调试信息存储
debug_info = {
    'app_start_time': None,
    'screen_transitions': [],
    'errors': [],
    'hardware_status': {}
}

class DebugLogger:
    """调试日志类"""
    @staticmethod
    def log(message, level='INFO'):
        timestamp = Clock.get_time()
        log_msg = f"[{level}] {timestamp:.2f}s: {message}"
        print(log_msg)
        Logger.info(log_msg)
        if level == 'ERROR':
            debug_info['errors'].append(log_msg)
    
    @staticmethod
    def log_error(error, context=''):
        error_msg = f"{context}: {str(error)}"
        DebugLogger.log(error_msg, 'ERROR')
        DebugLogger.log(traceback.format_exc(), 'ERROR')

class HardwareChecker:
    """硬件检测类"""
    @staticmethod
    def check_nfc():
        """检查NFC支持"""
        try:
            from plyer import nfc
            # 尝试获取NFC状态
            nfc_status = {
                'available': True,
                'enabled': True,
                'message': 'NFC功能可用'
            }
            DebugLogger.log('NFC检测: 支持')
            return nfc_status
        except ImportError:
            nfc_status = {
                'available': False,
                'enabled': False,
                'message': '未安装plyer库，NFC功能不可用'
            }
            DebugLogger.log('NFC检测: 不支持 - 未安装plyer库', 'ERROR')
            return nfc_status
        except Exception as e:
            nfc_status = {
                'available': False,
                'enabled': False,
                'message': f'NFC检测失败: {str(e)}'
            }
            DebugLogger.log_error(e, 'NFC检测')
            return nfc_status
    
    @staticmethod
    def check_camera():
        """检查摄像头支持"""
        try:
            from kivy.uix.camera import Camera
            camera_status = {
                'available': True,
                'message': '摄像头功能可用'
            }
            DebugLogger.log('摄像头检测: 支持')
            return camera_status
        except Exception as e:
            camera_status = {
                'available': False,
                'message': f'摄像头检测失败: {str(e)}'
            }
            DebugLogger.log_error(e, '摄像头检测')
            return camera_status
    
    @staticmethod
    def check_microphone():
        """检查麦克风支持"""
        try:
            from plyer import audio
            mic_status = {
                'available': True,
                'message': '麦克风功能可用'
            }
            DebugLogger.log('麦克风检测: 支持')
            return mic_status
        except ImportError:
            mic_status = {
                'available': False,
                'message': '未安装plyer库，麦克风功能不可用'
            }
            DebugLogger.log('麦克风检测: 不支持 - 未安装plyer库', 'ERROR')
            return mic_status
        except Exception as e:
            mic_status = {
                'available': False,
                'message': f'麦克风检测失败: {str(e)}'
            }
            DebugLogger.log_error(e, '麦克风检测')
            return mic_status
    
    @staticmethod
    def check_all_hardware():
        """检查所有硬件"""
        DebugLogger.log('开始检测硬件...')
        debug_info['hardware_status'] = {
            'nfc': HardwareChecker.check_nfc(),
            'camera': HardwareChecker.check_camera(),
            'microphone': HardwareChecker.check_microphone()
        }
        DebugLogger.log('硬件检测完成')
        return debug_info['hardware_status']

class StatusCLabel(CLabel):
    """状态标签组件"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.status_types = {
            'normal': (0.3, 0.3, 0.3, 1),      # 灰色
            'success': (0.2, 0.7, 0.3, 1),     # 绿色
            'warning': (0.9, 0.6, 0.2, 1),     # 橙色
            'error': (0.9, 0.2, 0.2, 1),       # 红色
            'info': (0.2, 0.6, 0.9, 1)         # 蓝色
        }
    
    def set_status(self, text, status_type='normal'):
        self.text = text
        self.color = self.status_types.get(status_type, self.status_types['normal'])
        DebugLogger.log(f'状态更新: {text} [{status_type}]')

class HomeScreen(Screen):
    """首页"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        DebugLogger.log('初始化首页')
        self.build_ui()
        # 延迟检测硬件
        Clock.schedule_once(self.check_hardware, 0.5)
    
    def build_ui(self):
        main_layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        # 标题
        title = CLabel(
            text='就诊数据采集系统',
            font_size='28sp',
            bold=True,
            color=(0.2, 0.4, 0.8, 1),
            size_hint_y=None,
            height=60
        )
        main_layout.add_widget(title)
        
        # 副标题
        subtitle = CLabel(
            text='Medical Data Collection System',
            font_size='14sp',
            color=(0.5, 0.5, 0.5, 1),
            size_hint_y=None,
            height=30
        )
        main_layout.add_widget(subtitle)
        
        # 硬件状态显示区域
        self.hardware_status_label = StatusCLabel(
            text='正在检测硬件...',
            font_size='12sp',
            size_hint_y=None,
            height=60
        )
        main_layout.add_widget(self.hardware_status_label)
        
        # 功能按钮
        functions = [
            ('📱 NFC身份验证', 'nfc', 'nfc'),
            ('📷 摄像头识别', 'camera', 'camera'),
            ('🎤 症状语音记录', 'voice', 'microphone'),
            ('📋 数据汇总', 'summary', None)
        ]
        
        for text, screen_name, hardware_key in functions:
            btn = CButton(
                text=text,
                font_size='18sp',
                size_hint_y=None,
                height=70,
                background_color=(0.2, 0.6, 0.9, 1),
                color=(1, 1, 1, 1)
            )
            btn.bind(on_press=lambda x, name=screen_name, hw=hardware_key: 
                     self.go_to_screen(name, hw))
            main_layout.add_widget(btn)
        
        # 调试信息按钮
        debug_btn = CButton(
            text='🔧 查看调试信息',
            font_size='14sp',
            size_hint_y=None,
            height=40,
            background_color=(0.5, 0.5, 0.5, 1)
        )
        debug_btn.bind(on_press=self.show_debug_info)
        main_layout.add_widget(debug_btn)
        
        # 状态显示
        self.status_label = StatusCLabel(
            text='就绪',
            font_size='16sp',
            size_hint_y=None,
            height=40
        )
        main_layout.add_widget(self.status_label)
        
        self.add_widget(main_layout)
        DebugLogger.log('首页UI构建完成')
    
    def check_hardware(self, dt):
        """检测硬件状态"""
        try:
            hardware_status = HardwareChecker.check_all_hardware()
            
            # 构建状态文本
            status_parts = []
            for hw_name, status in hardware_status.items():
                icon = '✓' if status['available'] else '✗'
                status_parts.append(f"{icon} {hw_name.upper()}")
            
            status_text = ' | '.join(status_parts)
            
            if all(s['available'] for s in hardware_status.values()):
                self.hardware_status_label.set_status(status_text, 'success')
                self.status_label.set_status('所有硬件检测通过', 'success')
            else:
                self.hardware_status_label.set_status(status_text, 'warning')
                unavailable = [k for k, v in hardware_status.items() if not v['available']]
                self.status_label.set_status(f"警告: {', '.join(unavailable)} 不可用", 'warning')
                
        except Exception as e:
            DebugLogger.log_error(e, '硬件检测')
            self.hardware_status_label.set_status('硬件检测失败', 'error')
            self.status_label.set_status('硬件检测异常', 'error')
    
    def go_to_screen(self, screen_name, hardware_key=None):
        """跳转到指定页面"""
        try:
            DebugLogger.log(f'跳转页面: {screen_name}')
            
            # 检查硬件是否可用
            if hardware_key and hardware_key in debug_info['hardware_status']:
                hw_status = debug_info['hardware_status'][hardware_key]
                if not hw_status['available']:
                    self.status_label.set_status(
                        f'{hardware_key.upper()} 不可用: {hw_status["message"]}', 
                        'error'
                    )
                    DebugLogger.log(f'{hardware_key} 不可用，阻止跳转', 'WARNING')
                    return
            
            debug_info['screen_transitions'].append({
                'from': 'home',
                'to': screen_name,
                'time': Clock.get_time()
            })
            
            self.manager.current = screen_name
            self.status_label.set_status(f'进入 {screen_name} 页面', 'info')
            
        except Exception as e:
            DebugLogger.log_error(e, f'跳转页面 {screen_name}')
            self.status_label.set_status(f'跳转失败: {str(e)}', 'error')
    
    def show_debug_info(self, instance):
        """显示调试信息"""
        try:
            debug_text = "=== 调试信息 ===\n\n"
            
            # 硬件状态
            debug_text += "【硬件状态】\n"
            for hw_name, status in debug_info['hardware_status'].items():
                debug_text += f"{hw_name}: {status['message']}\n"
            
            debug_text += f"\n【页面跳转记录】({len(debug_info['screen_transitions'])}次)\n"
            for transition in debug_info['screen_transitions'][-5:]:  # 只显示最近5次
                debug_text += f"{transition['from']} -> {transition['to']}\n"
            
            debug_text += f"\n【错误记录】({len(debug_info['errors'])}条)\n"
            for error in debug_info['errors'][-5:]:  # 只显示最近5条
                debug_text += f"{error}\n"
            
            # 创建调试信息弹窗
            self.show_debug_popup(debug_text)
            
        except Exception as e:
            DebugLogger.log_error(e, '显示调试信息')
    
    def show_debug_popup(self, text):
        """显示调试信息弹窗"""
        from kivy.uix.popup import Popup
        
        content = BoxLayout(orientation='vertical', padding=10)
        
        scroll = ScrollView()
        label = CLabel(
            text=text,
            font_size='12sp',
            size_hint_y=None,
            text_size=(300, None)
        )
        label.bind(texture_size=lambda instance, value: setattr(instance, 'height', value[1]))
        scroll.add_widget(label)
        content.add_widget(scroll)
        
        close_btn = CButton(
            text='关闭',
            size_hint_y=None,
            height=40
        )
        
        popup = Popup(
            title='调试信息',
            content=content,
            size_hint=(0.9, 0.8)
        )
        
        close_btn.bind(on_press=popup.dismiss)
        content.add_widget(close_btn)
        
        popup.open()
        DebugLogger.log('打开调试信息弹窗')

class NFCScreen(Screen):
    """NFC页面"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        DebugLogger.log('初始化NFC页面')
        self.nfc_data = None
        self.build_ui()
    
    def build_ui(self):
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        title = CLabel(
            text='NFC身份验证',
            font_size='24sp',
            bold=True,
            color=(0.2, 0.4, 0.8, 1),
            size_hint_y=None,
            height=50
        )
        layout.add_widget(title)
        
        # 硬件状态提示
        self.hw_status_label = StatusCLabel(
            text='检查NFC状态...',
            font_size='14sp',
            size_hint_y=None,
            height=40
        )
        layout.add_widget(self.hw_status_label)
        
        # 操作说明
        self.instruction_label = CLabel(
            text='请将身份证靠近手机背面',
            font_size='16sp',
            color=(0.4, 0.4, 0.4, 1),
            size_hint_y=None,
            height=40
        )
        layout.add_widget(self.instruction_label)
        
        # 状态显示
        self.status_label = StatusCLabel(
            text='等待操作...',
            font_size='18sp',
            size_hint_y=None,
            height=60
        )
        layout.add_widget(self.status_label)
        
        # 扫描按钮
        self.scan_btn = CButton(
            text='开始扫描',
            font_size='20sp',
            size_hint_y=None,
            height=60,
            background_color=(0.2, 0.7, 0.3, 1)
        )
        self.scan_btn.bind(on_press=self.start_scan)
        layout.add_widget(self.scan_btn)
        
        # 结果显示区域
        result_title = CLabel(
            text='读取结果：',
            font_size='16sp',
            bold=True,
            color=(0.3, 0.3, 0.3, 1),
            size_hint_y=None,
            height=30
        )
        layout.add_widget(result_title)
        
        self.result_text = CTextInput(
            text='',
            font_size='14sp',
            multiline=True,
            size_hint_y=None,
            height=150,
            readonly=True
        )
        layout.add_widget(self.result_text)
        
        # 返回按钮
        back_btn = CButton(
            text='← 返回首页',
            font_size='16sp',
            size_hint_y=None,
            height=50,
            background_color=(0.5, 0.5, 0.5, 1)
        )
        back_btn.bind(on_press=self.go_back)
        layout.add_widget(back_btn)
        
        self.add_widget(layout)
        
        # 检查NFC状态
        Clock.schedule_once(self.check_nfc_status, 0.1)
        DebugLogger.log('NFC页面UI构建完成')
    
    def check_nfc_status(self, dt):
        """检查NFC状态"""
        try:
            nfc_status = debug_info['hardware_status'].get('nfc', {})
            
            if not nfc_status.get('available', False):
                self.hw_status_label.set_status(
                    f'NFC不可用: {nfc_status.get("message", "未知错误")}', 
                    'error'
                )
                self.scan_btn.disabled = True
                self.scan_btn.background_color = (0.5, 0.5, 0.5, 1)
                self.status_label.set_status('NFC功能不可用', 'error')
                DebugLogger.log('NFC不可用，禁用扫描按钮', 'WARNING')
            else:
                self.hw_status_label.set_status('NFC就绪', 'success')
                DebugLogger.log('NFC就绪')
                
        except Exception as e:
            DebugLogger.log_error(e, '检查NFC状态')
            self.hw_status_label.set_status('NFC状态检查失败', 'error')
    
    def start_scan(self, instance):
        """开始扫描"""
        try:
            DebugLogger.log('开始NFC扫描')
            self.status_label.set_status('正在扫描...', 'info')
            self.scan_btn.disabled = True
            self.scan_btn.text = '扫描中...'
            
            # 模拟扫描过程
            Clock.schedule_once(self.simulate_scan, 2)
            
        except Exception as e:
            DebugLogger.log_error(e, '开始扫描')
            self.status_label.set_status(f'扫描失败: {str(e)}', 'error')
            self.scan_btn.disabled = False
            self.scan_btn.text = '开始扫描'
    
    def simulate_scan(self, dt):
        """模拟扫描结果"""
        try:
            DebugLogger.log('模拟NFC扫描完成')
            
            # 模拟数据
            self.nfc_data = {
                'name': '张三',
                'id_number': '110101199001011234',
                'gender': '男',
                'birth_date': '1990-01-01',
                'address': '北京市朝阳区'
            }
            
            # 显示结果
            result_text = f"""姓名：{self.nfc_data['name']}
身份证号：{self.nfc_data['id_number']}
性别：{self.nfc_data['gender']}
出生日期：{self.nfc_data['birth_date']}
地址：{self.nfc_data['address']}"""
            
            self.result_text.text = result_text
            self.status_label.set_status('扫描成功！', 'success')
            self.instruction_label.text = '身份证信息读取完成'
            
            self.scan_btn.text = '重新扫描'
            self.scan_btn.disabled = False
            
            DebugLogger.log('NFC扫描成功，数据已显示')
            
        except Exception as e:
            DebugLogger.log_error(e, '模拟扫描')
            self.status_label.set_status(f'读取失败: {str(e)}', 'error')
            self.scan_btn.text = '重新扫描'
            self.scan_btn.disabled = False
    
    def go_back(self, instance):
        """返回首页"""
        try:
            DebugLogger.log('从NFC页面返回首页')
            self.manager.current = 'home'
            # 重置状态
            self.status_label.set_status('等待操作...', 'normal')
            self.result_text.text = ''
            self.scan_btn.text = '开始扫描'
            self.scan_btn.disabled = False
            self.instruction_label.text = '请将身份证靠近手机背面'
        except Exception as e:
            DebugLogger.log_error(e, '返回首页')

class CameraScreen(Screen):
    """摄像头页面"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        DebugLogger.log('初始化摄像头页面')
        self.build_ui()
    
    def build_ui(self):
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        title = CLabel(
            text='摄像头识别',
            font_size='24sp',
            bold=True,
            color=(0.2, 0.4, 0.8, 1),
            size_hint_y=None,
            height=50
        )
        layout.add_widget(title)
        
        # 硬件状态提示
        self.hw_status_label = StatusCLabel(
            text='检查摄像头状态...',
            font_size='14sp',
            size_hint_y=None,
            height=40
        )
        layout.add_widget(self.hw_status_label)
        
        # 摄像头预览区域（模拟）
        self.preview_label = CLabel(
            text='[摄像头预览区域]\n\n点击拍照按钮进行人脸识别',
            font_size='16sp',
            color=(0.5, 0.5, 0.5, 1),
            size_hint_y=None,
            height=200
        )
        layout.add_widget(self.preview_label)
        
        # 拍照按钮
        self.capture_btn = CButton(
            text='📷 拍照识别',
            font_size='20sp',
            size_hint_y=None,
            height=60,
            background_color=(0.2, 0.7, 0.3, 1)
        )
        self.capture_btn.bind(on_press=self.capture)
        layout.add_widget(self.capture_btn)
        
        # 识别结果
        self.result_label = StatusCLabel(
            text='',
            font_size='16sp',
            size_hint_y=None,
            height=100
        )
        layout.add_widget(self.result_label)
        
        back_btn = CButton(
            text='← 返回首页',
            font_size='16sp',
            size_hint_y=None,
            height=50,
            background_color=(0.5, 0.5, 0.5, 1)
        )
        back_btn.bind(on_press=self.go_back)
        layout.add_widget(back_btn)
        
        self.add_widget(layout)
        
        # 检查摄像头状态
        Clock.schedule_once(self.check_camera_status, 0.1)
        DebugLogger.log('摄像头页面UI构建完成')
    
    def check_camera_status(self, dt):
        """检查摄像头状态"""
        try:
            camera_status = debug_info['hardware_status'].get('camera', {})
            
            if not camera_status.get('available', False):
                self.hw_status_label.set_status(
                    f'摄像头不可用: {camera_status.get("message", "未知错误")}',
                    'error'
                )
                self.capture_btn.disabled = True
                self.capture_btn.background_color = (0.5, 0.5, 0.5, 1)
                self.preview_label.text = '[摄像头不可用]\n\n请检查设备权限'
                DebugLogger.log('摄像头不可用，禁用拍照按钮', 'WARNING')
            else:
                self.hw_status_label.set_status('摄像头就绪', 'success')
                DebugLogger.log('摄像头就绪')
                
        except Exception as e:
            DebugLogger.log_error(e, '检查摄像头状态')
            self.hw_status_label.set_status('摄像头状态检查失败', 'error')
    
    def capture(self, instance):
        """拍照识别"""
        try:
            DebugLogger.log('开始拍照识别')
            self.capture_btn.disabled = True
            self.capture_btn.text = '识别中...'
            self.preview_label.text = '[正在识别...]'
            
            # 模拟识别过程
            Clock.schedule_once(self.simulate_recognition, 2)
            
        except Exception as e:
            DebugLogger.log_error(e, '拍照识别')
            self.result_label.set_status(f'识别失败: {str(e)}', 'error')
            self.capture_btn.disabled = False
            self.capture_btn.text = '📷 拍照识别'
    
    def simulate_recognition(self, dt):
        """模拟识别结果"""
        try:
            DebugLogger.log('人脸识别完成')
            
            self.result_label.set_status('✓ 人脸识别成功\n匹配度：98.5%', 'success')
            self.preview_label.text = '[识别完成]\n\n人脸特征已提取'
            
            self.capture_btn.text = '📷 重新拍照'
            self.capture_btn.disabled = False
            
        except Exception as e:
            DebugLogger.log_error(e, '模拟识别')
            self.result_label.set_status(f'识别失败: {str(e)}', 'error')
            self.capture_btn.text = '📷 重新拍照'
            self.capture_btn.disabled = False
    
    def go_back(self, instance):
        """返回首页"""
        try:
            DebugLogger.log('从摄像头页面返回首页')
            self.manager.current = 'home'
            self.result_label.text = ''
            self.capture_btn.text = '📷 拍照识别'
            self.capture_btn.disabled = False
            self.preview_label.text = '[摄像头预览区域]\n\n点击拍照按钮进行人脸识别'
        except Exception as e:
            DebugLogger.log_error(e, '返回首页')

class VoiceScreen(Screen):
    """语音页面"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        DebugLogger.log('初始化语音页面')
        self.is_recording = False
        self.build_ui()
    
    def build_ui(self):
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        title = CLabel(
            text='症状语音记录',
            font_size='24sp',
            bold=True,
            color=(0.2, 0.4, 0.8, 1),
            size_hint_y=None,
            height=50
        )
        layout.add_widget(title)
        
        # 硬件状态提示
        self.hw_status_label = StatusCLabel(
            text='检查麦克风状态...',
            font_size='14sp',
            size_hint_y=None,
            height=40
        )
        layout.add_widget(self.hw_status_label)
        
        # 录音按钮
        self.record_btn = CButton(
            text='🎤 开始录音',
            font_size='20sp',
            size_hint_y=None,
            height=80,
            background_color=(0.9, 0.2, 0.2, 1)
        )
        self.record_btn.bind(on_press=self.toggle_record)
        layout.add_widget(self.record_btn)
        
        # 录音状态
        self.status_label = StatusCLabel(
            text='点击按钮开始录音',
            font_size='16sp',
            size_hint_y=None,
            height=40
        )
        layout.add_widget(self.status_label)
        
        # 转写结果显示
        result_title = CLabel(
            text='语音转文字结果：',
            font_size='16sp',
            bold=True,
            color=(0.3, 0.3, 0.3, 1),
            size_hint_y=None,
            height=30
        )
        layout.add_widget(result_title)
        
        self.result_text = CTextInput(
            text='',
            font_size='14sp',
            multiline=True,
            size_hint_y=None,
            height=150
        )
        layout.add_widget(self.result_text)
        
        back_btn = CButton(
            text='← 返回首页',
            font_size='16sp',
            size_hint_y=None,
            height=50,
            background_color=(0.5, 0.5, 0.5, 1)
        )
        back_btn.bind(on_press=self.go_back)
        layout.add_widget(back_btn)
        
        self.add_widget(layout)
        
        # 检查麦克风状态
        Clock.schedule_once(self.check_mic_status, 0.1)
        DebugLogger.log('语音页面UI构建完成')
    
    def check_mic_status(self, dt):
        """检查麦克风状态"""
        try:
            mic_status = debug_info['hardware_status'].get('microphone', {})
            
            if not mic_status.get('available', False):
                self.hw_status_label.set_status(
                    f'麦克风不可用: {mic_status.get("message", "未知错误")}',
                    'error'
                )
                self.record_btn.disabled = True
                self.record_btn.background_color = (0.5, 0.5, 0.5, 1)
                self.status_label.set_status('麦克风功能不可用', 'error')
                DebugLogger.log('麦克风不可用，禁用录音按钮', 'WARNING')
            else:
                self.hw_status_label.set_status('麦克风就绪', 'success')
                DebugLogger.log('麦克风就绪')
                
        except Exception as e:
            DebugLogger.log_error(e, '检查麦克风状态')
            self.hw_status_label.set_status('麦克风状态检查失败', 'error')
    
    def toggle_record(self, instance):
        """切换录音状态"""
        try:
            if not self.is_recording:
                DebugLogger.log('开始录音')
                self.start_recording()
            else:
                DebugLogger.log('停止录音')
                self.stop_recording()
                
        except Exception as e:
            DebugLogger.log_error(e, '切换录音状态')
            self.status_label.set_status(f'录音操作失败: {str(e)}', 'error')
    
    def start_recording(self):
        """开始录音"""
        self.is_recording = True
        self.record_btn.text = '⏹ 停止录音'
        self.record_btn.background_color = (0.9, 0.5, 0.2, 1)
        self.status_label.set_status('正在录音...', 'info')
        DebugLogger.log('录音中...')
    
    def stop_recording(self):
        """停止录音"""
        self.is_recording = False
        self.record_btn.text = '🎤 开始录音'
        self.record_btn.background_color = (0.9, 0.2, 0.2, 1)
        self.status_label.set_status('录音完成，正在转写...', 'info')
        
        # 模拟转写
        Clock.schedule_once(self.simulate_transcription, 1)
    
    def simulate_transcription(self, dt):
        """模拟语音转文字"""
        try:
            DebugLogger.log('语音转文字完成')
            
            transcription = '''患者主诉：最近一周感觉头晕乏力，伴有轻微咳嗽，体温略有升高，食欲下降。'''
            
            self.result_text.text = transcription
            self.status_label.set_status('转写完成！', 'success')
            
        except Exception as e:
            DebugLogger.log_error(e, '语音转写')
            self.status_label.set_status(f'转写失败: {str(e)}', 'error')
    
    def go_back(self, instance):
        """返回首页"""
        try:
            DebugLogger.log('从语音页面返回首页')
            self.manager.current = 'home'
            
            # 重置状态
            if self.is_recording:
                self.is_recording = False
            
            self.record_btn.text = '🎤 开始录音'
            self.record_btn.background_color = (0.9, 0.2, 0.2, 1)
            self.status_label.set_status('点击按钮开始录音', 'normal')
            self.result_text.text = ''
            
        except Exception as e:
            DebugLogger.log_error(e, '返回首页')

class SummaryScreen(Screen):
    """数据汇总页面"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        DebugLogger.log('初始化数据汇总页面')
        self.build_ui()
    
    def build_ui(self):
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        title = CLabel(
            text='数据汇总',
            font_size='24sp',
            bold=True,
            color=(0.2, 0.4, 0.8, 1),
            size_hint_y=None,
            height=50
        )
        layout.add_widget(title)
        
        # 数据概览
        summary_text = '''患者信息：
• 姓名：张三
• 身份证号：110101199001011234
• 性别：男

症状记录：
• 头晕乏力
• 轻微咳嗽
• 体温升高
• 食欲下降

采集时间：2026-03-12 14:30'''
        
        summary_label = CLabel(
            text=summary_text,
            font_size='14sp',
            color=(0.2, 0.2, 0.2, 1),
            size_hint_y=None,
            height=250
        )
        layout.add_widget(summary_label)
        
        # 上传按钮
        self.upload_btn = CButton(
            text='☁️ 上传数据',
            font_size='20sp',
            size_hint_y=None,
            height=60,
            background_color=(0.2, 0.6, 0.9, 1)
        )
        self.upload_btn.bind(on_press=self.upload_data)
        layout.add_widget(self.upload_btn)
        
        # 上传状态
        self.upload_status = StatusCLabel(
            text='',
            font_size='16sp',
            size_hint_y=None,
            height=40
        )
        layout.add_widget(self.upload_status)
        
        back_btn = CButton(
            text='← 返回首页',
            font_size='16sp',
            size_hint_y=None,
            height=50,
            background_color=(0.5, 0.5, 0.5, 1)
        )
        back_btn.bind(on_press=self.go_back)
        layout.add_widget(back_btn)
        
        self.add_widget(layout)
        DebugLogger.log('数据汇总页面UI构建完成')
    
    def upload_data(self, instance):
        """上传数据"""
        try:
            DebugLogger.log('开始上传数据')
            self.upload_btn.disabled = True
            self.upload_btn.text = '上传中...'
            self.upload_status.set_status('正在连接服务器...', 'info')
            
            # 模拟上传
            Clock.schedule_once(self.simulate_upload, 2)
            
        except Exception as e:
            DebugLogger.log_error(e, '上传数据')
            self.upload_status.set_status(f'上传失败: {str(e)}', 'error')
            self.upload_btn.disabled = False
            self.upload_btn.text = '☁️ 重新上传'
    
    def simulate_upload(self, dt):
        """模拟上传"""
        try:
            DebugLogger.log('数据上传成功')
            self.upload_status.set_status('✓ 数据上传成功！', 'success')
            self.upload_btn.text = '☁️ 上传完成'
            self.upload_btn.disabled = False
            
        except Exception as e:
            DebugLogger.log_error(e, '模拟上传')
            self.upload_status.set_status(f'上传失败: {str(e)}', 'error')
            self.upload_btn.disabled = False
            self.upload_btn.text = '☁️ 重新上传'
    
    def go_back(self, instance):
        """返回首页"""
        try:
            DebugLogger.log('从数据汇总页面返回首页')
            self.manager.current = 'home'
            self.upload_status.text = ''
            self.upload_btn.text = '☁️ 上传数据'
            self.upload_btn.disabled = False
        except Exception as e:
            DebugLogger.log_error(e, '返回首页')

class MedicalApp(App):
    """主应用类"""
    def build(self):
        DebugLogger.log('应用启动')
        debug_info['app_start_time'] = Clock.get_time()
        
        try:
            sm = ScreenManager()
            sm.add_widget(HomeScreen(name='home'))
            sm.add_widget(NFCScreen(name='nfc'))
            sm.add_widget(CameraScreen(name='camera'))
            sm.add_widget(VoiceScreen(name='voice'))
            sm.add_widget(SummaryScreen(name='summary'))
            
            DebugLogger.log('所有页面加载完成')
            return sm
            
        except Exception as e:
            DebugLogger.log_error(e, '应用构建')
            raise
    
    def on_start(self):
        DebugLogger.log('应用开始运行')
    
    def on_stop(self):
        DebugLogger.log('应用停止')
        # 输出最终调试信息
        print("\n=== 最终调试信息 ===")
        print(f"页面跳转次数: {len(debug_info['screen_transitions'])}")
        print(f"错误次数: {len(debug_info['errors'])}")
        if debug_info['errors']:
            print("错误列表:")
            for error in debug_info['errors']:
                print(f"  - {error}")

if __name__ == '__main__':
    try:
        MedicalApp().run()
    except Exception as e:
        DebugLogger.log_error(e, '应用运行')
        raise
