from abc import ABC, abstractmethod

import customtkinter as ctk

from tools.config import Config


class AppABC(ctk.CTk, ABC):
    @property
    @abstractmethod
    def config(self) -> Config:
        pass

    @config.setter
    @abstractmethod
    def config(self, value):
        pass


class FrameABC(ctk.CTkFrame, ABC):
    @property
    @abstractmethod
    def master(self) -> AppABC:
        pass

    @master.setter
    @abstractmethod
    def master(self, value):
        pass
