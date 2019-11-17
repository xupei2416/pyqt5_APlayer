import ctypes
import sys

import win32con
import win32gui
from PyQt5 import QtGui
from PyQt5.QtWidgets import QWidget, QApplication


class VideoWindow(QWidget):

    def __init__(self):
        super(VideoWindow, self).__init__()

        self.resize(960, 540)

        # 定义一个函数的回调，用于传递给dll方法
        # 此处必须使用WINFUNCTYPE方法，CFUNCTYPE方法会导致程序崩溃
        # 共有8个回调函数，详细使用方法见APlayer开发文档
        self.onMessageFunType = ctypes.WINFUNCTYPE(ctypes.HRESULT, ctypes.c_long, ctypes.c_long, ctypes.c_long)
        self.onMessageCallback = self.onMessageFunType(self.onMessage)

        self.onStateChangedFunType = ctypes.WINFUNCTYPE(ctypes.HRESULT, ctypes.c_long, ctypes.c_long)
        self.onStateChangedCallback = self.onStateChangedFunType(self.onStateChanged)

        self.onOpenSuccessFunType = ctypes.WINFUNCTYPE(ctypes.HRESULT)
        self.onOpenSuccessCallback = self.onOpenSuccessFunType(self.onOpenSuccess)

        self.onSeekCompletedFunType = ctypes.WINFUNCTYPE(ctypes.HRESULT, ctypes.c_long)
        self.onSeekCompletedCallback = self.onSeekCompletedFunType(self.onSeekCompleted)

        self.onBufferFunType = ctypes.WINFUNCTYPE(ctypes.HRESULT, ctypes.c_long)
        self.onBufferCallback = self.onBufferFunType(self.onBuffer)

        self.onVideoSizeChangedFunType = ctypes.WINFUNCTYPE(ctypes.HRESULT)
        self.onVideoSizeChangedCallback = self.onVideoSizeChangedFunType(self.onVideoSizeChanged)

        self.onDownloadCodecFunType = ctypes.WINFUNCTYPE(ctypes.HRESULT, ctypes.c_int)
        self.onDownloadCodecCallback = self.onDownloadCodecFunType(self.onDownloadCodec)

        self.onEventFunType = ctypes.WINFUNCTYPE(ctypes.HRESULT, ctypes.c_long, ctypes.c_long)
        self.onEventCallback = self.onEventFunType(self.onEvent)

        # 采用APlayerCaller.dll实现COM组件免注册
        self.library = ctypes.windll.LoadLibrary("APlayerCaller.dll")
        # 创建APlayer实例，并返回实例（int）
        self.aPlayer = self.library.APlayer_Create(int(self.winId()), 0, 0, self.width(), self.height(),
                                                   self.onMessageCallback, self.onStateChangedCallback,
                                                   self.onOpenSuccessCallback, self.onSeekCompletedCallback,
                                                   self.onBufferCallback, self.onVideoSizeChangedCallback,
                                                   self.onDownloadCodecCallback, self.onEventCallback)

        # 取消默认Logo
        self.library.APlayer_SetCustomLogo(self.aPlayer, -1)
        # 设置播放完毕不自动关闭
        self.library.APlayer_SetConfigA(self.aPlayer, 120, "1")
        # 设置为单曲循环播放
        self.library.APlayer_SetConfigA(self.aPlayer, 119, "1")

        print(self.library.APlayer_GetVersion(self.aPlayer))

        """
            APlayerCaller.dll可调用的函数如下：
            1.创建APlayer实例：APlayer_Create(int, int, int, int, int, int, int, int, int, int, int, int, int)
                参数：APlayer播放器窗口所依附的窗口句柄、APlayer播放器窗口初始化x坐标、APlayer播放器窗口初始化y坐标、APlayer播放器窗口初始化宽、APlayer播放器窗口初始化高、各回调函数的指针（8个）
                返回：int
            2.打开视频文件：APlayer_OpenW(int, str)
                参数：APlayer实例、视频地址（支持所有视频文件格式，包括http、视频流等）
            3.参数设置：APlayer_SetConfigA(int, int, str)
                参数：APlayer实例、configId、值
                具体设置参考APlayer开发文档
            4.获取版本信息：APlayer_GetVersion(int)
                参数：APlayer实例，返回数据为指针，需通过str(ctypes.string_at(value), encoding="utf-8"))转成字符串
            5.取视频宽度：APlayer_GetVideoWidth(int)
                参数：APlayer实例
            6.取视频高度：APlayer_GetVideoHeight(int)
                参数：APlayer实例
            7.销毁实例：APlayer_Destroy(int)
                参数：APlayer实例
            8.关闭视频：APlayer_Close(int)
                参数：APlayer实例
            9.播放视频：APlayer_Play(int)
                参数：APlayer实例
            10.暂停视频：APlayer_Pause(int)
                参数：APlayer实例
            11.设置播放器屏保画面：APlayer_SetCustomLogo(int, int)
                参数：APlayer实例、位图句柄
            12.取当前播放状态：APlayer_GetState(int)
                参数：APlayer实例（参考开发文档）
            13.取视频总时长：APlayer_GetDuration(int)
                参数：APlayer实例
            14.取当前播放位置：APlayer_GetPosition(int)
                参数：APlayer实例
            15.取播放音量：APlayer_GetVolumn(int)
                参数：APlayer实例
            16.设置播放音量：APlayer_SetVolumn(int, int)
                参数：APlayer实例、音量（0-1000，100就满了，大于100可再加大）
            17.查询播放器当前是否处于设置播放进度过程：APlayer_IsSeeking(int)
                参数：APlayer实例
            17.获取APlayer引擎播放网络文件时的数据缓冲进度：APlayer_GetBufferProgress(int)
                参数：APlayer实例
            18.获取APlayer引擎的设置：APlayer_GetConfig(int, int)
                参数：APlayer实例、configId
            19.获取播放器窗口句柄：APlayer_GetWindow(int)
                参数：APlayer实例
        """

    def showEvent(self, event: QtGui.QShowEvent) -> None:
        super(VideoWindow, self).showEvent(event)
        self.library.APlayer_OpenW(self.aPlayer, "F:/1.mp4")

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        super(VideoWindow, self).closeEvent(event)
        if self.aPlayer > 0:
            self.library.APlayer_Destroy(self.aPlayer)
        self.aPlayer = 0
        pass

    def resizeEvent(self, event: QtGui.QResizeEvent) -> None:
        super(VideoWindow, self).resizeEvent(event)
        if self.aPlayer > 0:
            aPlayerHandler = self.library.APlayer_GetWindow(self.aPlayer)
            win32gui.SetWindowPos(aPlayerHandler, 0, 0, 0, self.width(), self.height(), win32con.SWP_NOZORDER)

    def videoStatusChanged(self, status):
        pass

    def onMessage(self, a: int, b: int, c: int) -> int:
        print(a, b, c)
        return 1

    def onStateChanged(self, oldCode: int, newCode: int) -> int:
        print(oldCode, newCode)
        return 1

    def onOpenSuccess(self) -> int:
        return 1

    def onSeekCompleted(self, a: int) -> int:
        print(a)
        return 1

    def onBuffer(self, a: int) -> int:
        print(a)
        return 1

    def onVideoSizeChanged(self) -> int:
        return 1

    # 触发缺失解码器回调函数
    def onDownloadCodec(self, pathAddress: int) -> int:
        # 此处添加下载解码器代码
        print("缺少解码器：" + str(ctypes.string_at(pathAddress), encoding="utf-8"))
        # 使用此方法通知APlayer解码器已经下载完毕，继续播放
        self.library.APlayer_SetConfigA(self.aPlayer, 19, "1")
        return 1

    def onEvent(self, a: int, b: int) -> int:
        print(a, b)
        return 1


if __name__ == "__main__":
    # 如果程序不是以管理员方式运行，则以管理员方式重新运行
    app = QApplication(sys.argv)
    videoWindow = VideoWindow()
    videoWindow.show()
    sys.exit(app.exec_())
