import tkinter as tk
from datetime import datetime
import threading
import pygame
from typing import Callable

from account import Account

class StatusGUI(Account):
    def __init__(self):
        self.root = tk.Tk()

        self.root.title('Mining System Status Automatic Checker (MSSAC) by Jiwon')
        self.root.geometry('495x230+200+200')
        self.root.resizable(True, True)
        
        pygame.init()
        pygame.mixer.init()
        self.start_sound = pygame.mixer.Sound('macintosh_startup_sound.wav')
        self.beep_sound= pygame.mixer.Sound('beep_sound.wav')
        
        self.num_of_account = 0
        self.time_str = tk.StringVar(self.root)
        self.last_check_time_str = tk.StringVar(self.root)
    
    def load(self, type_of_OS: str):
        curr_time_lbl_width: int
        last_check_time_lbl_width: int
        
        if type_of_OS == 'macOS':
            curr_time_lbl_width = 23
            last_check_time_lbl_width = 31
        elif type_of_OS == 'windows':
            curr_time_lbl_width = 30
            last_check_time_lbl_width = 40
        
        self.time_str.set('|----------Welcome----------|')
        self.last_check_time_str.set('|----------Welcome----------|')
        
        frame_times = tk.Frame(self.root)
        
        lbl_curr_time = tk.Label(frame_times, textvariable=self.time_str, width=curr_time_lbl_width, height=2, bg='blue', fg='yellow')
        lbl_curr_time.grid(row=0, column=0, sticky='w')
        
        lbl_last_check_time = tk.Label(frame_times, textvariable=self.last_check_time_str, width=last_check_time_lbl_width, height=2, bg='yellow', fg='blue')
        lbl_last_check_time.grid(row=0, column=1,sticky='w')
 
        frame_times.grid(row=0, column=0, sticky='w')
        
    def set_interval(self, func: Callable, sec: float):
        def func_wrapper():
            self.set_interval(func, sec)
            func()
        t = threading.Timer(sec, func_wrapper)
        t.start()
        return t
    
    def add_account(self, account: Account, type_of_OS: str):
        lbl_width: int;
        if type_of_OS == 'macOS':
            lbl_width = 45
        elif type_of_OS == 'windows':
            lbl_width = 60
        
        globals()[f'self.account_{self.num_of_account}']: Account = account  # account_{id}
        
        globals()[f'self.account_{self.num_of_account}_strVar'] = tk.StringVar(self.root)
        globals()[f'self.account_{self.num_of_account}_strVar'].set(f'여기에 계정 {self.num_of_account}의 상태가 표시됩니다.')
        
        globals()[f'self.account_{self.num_of_account}_isOk_strVar'] = tk.StringVar(self.root)
        globals()[f'self.account_{self.num_of_account}_isOk_strVar'].set('Start')
        
        globals()[f'self.account_{self.num_of_account}_frame'] = tk.Frame(self.root)
        
        globals()[f'self.account_{self.num_of_account}_lbl'] = tk.Label(globals()[f'self.account_{self.num_of_account}_frame'], textvariable=globals()[f'self.account_{self.num_of_account}_strVar'], width=lbl_width, height=2, bg='white', fg='black', anchor='w')
        globals()[f'self.account_{self.num_of_account}_lbl'].grid(row=0, column=0)
        
        globals()[f'self.account_{self.num_of_account}_isOk_lbl'] = tk.Label(globals()[f'self.account_{self.num_of_account}_frame'], textvariable=globals()[f'self.account_{self.num_of_account}_isOk_strVar'], width=9, height=2, bg='black', fg='white')
        globals()[f'self.account_{self.num_of_account}_isOk_lbl'].grid(row=0, column=1)
        
        globals()[f'self.account_{self.num_of_account}_frame'].grid(row=1 + self.num_of_account, column=0, sticky='w')
        
        self.num_of_account += 1
        
    def update_account_strVar(self, account_id: int):
        account = globals()[f'self.account_{account_id}']
        globals()[f'self.account_{account_id}'].update_status()
        globals()[f'self.account_{account_id}_strVar'].set(f'ID {account_id:<2} : {account.id:<10} || TTL {account.status['total']:<8,} ACT {account.status['active']:<8,} FLT {account.status['fault']:<8,} REV {account.status['recovery']:<8,}')
        
        if globals()[f'self.account_{account_id}'].status['fault'] > 0:  # if account.status has falut
            globals()[f'self.account_{account_id}_isOk_lbl'].config(bg='red', fg='yellow')
            globals()[f'self.account_{account_id}_isOk_strVar'].set(f'{globals()[f'self.account_{account_id}'].status['fault']} FAULT')
            self.beep_sound.play(-1, 30000)  # 30 seconds beep
        elif globals()[f'self.account_{account_id}'].status['fault'] == 0:  # if account.status has no falut
            globals()[f'self.account_{account_id}_isOk_lbl'].config(bg='green', fg='white')
            globals()[f'self.account_{account_id}_isOk_strVar'].set('NO FAULT')
            
    
    def start(self, type_of_OS: str):
        status_checking_duration = 120  # 2 minutes (=120 sec)
        
        def clock():
            now = datetime.now()
            self.time_str.set(f'현재시각: {now.strftime('%Y-%m-%d %H:%M:%S')}')
            nonlocal status_checking_duration
            status_checking_duration -= 1
            self.last_check_time_str.set(f'최근통신시각: {globals()[f'self.account_{self.num_of_account - 1}'].last_check_time} ({120 - status_checking_duration}초 전)')
            if status_checking_duration <= 0:
                status_checking_duration = 120
                for id in range(0, self.num_of_account):
                    self.update_account_strVar(id)

                    
        for id in range(0, self.num_of_account):
            self.update_account_strVar(id)
                    
        self.set_interval(clock, 1)
        
        self.load(type_of_OS)
        
        self.start_sound.play()
        
        self.root.mainloop()