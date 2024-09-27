import asyncio
import time
import time
import asyncio

class AsyncAlarm:
    def __init__(self, user, callback: callable = None):
        self.user = user
        self.alarms = []
        self.countdowns = []
        self.callback = callback
        self.running = False
        print()

    def set_alarm(self, hour, minute, message):
        print(f'Add alarm {hour}:{minute}')
        self.alarms.append((hour, minute, message))

    def set_countdown(self, seconds, message):
        print(f'Add countdown {seconds}s')
        self.countdowns.append((seconds, message))

    async def check_alarm(self):
        print(f'Alarm watchdog for {self.user} will active now.')
        while self.running:
            current_time = time.localtime()
            alarms_to_remove = []
            for alarm in self.alarms:
                if current_time.tm_hour == alarm[0] and current_time.tm_min == alarm[1]:
                    try:
                        if self.callback:
                            self.callback(alarm[2])
                    except Exception as e:
                        print(f"Error in alarm callback: {e}")
                    alarms_to_remove.append(alarm)
            for alarm in alarms_to_remove:
                self.alarms.remove(alarm)
            await asyncio.sleep(1)

    async def check_countdown(self):
        print(f'Countdown watchdog for {self.user} will active now.')
        while self.running:
            countdowns_to_update = []
            for countdown in self.countdowns:
                remaining_time, message = countdown
                if remaining_time <= 0:
                    try:
                        if self.callback:
                            self.callback(message)
                    except Exception as e:
                        print(f"Error in countdown callback: {e}")
                else:
                    countdowns_to_update.append((remaining_time - 1, message))
            self.countdowns = countdowns_to_update
            await asyncio.sleep(1)

    async def loop(self):
        self.running = True
        await asyncio.gather(
            self.check_alarm(),
            self.check_countdown()
        )

# 回調函數示例
def user1_callback(message):
    print(f"鬧鐘響了! 使用者: 1\n{message}")

def user2_callback(message):
    print(f"鬧鐘響了!  使用者: 2\n{message}")

# 使用示例
async def main():
    # 為兩個不同用戶創建鬧鐘實例
    alarm1 = AsyncAlarm("用戶1",user1_callback)
    alarm2 = AsyncAlarm("用戶2",user2_callback)

    # 設置鬧鐘和倒計時
    alarm1.set_alarm(23, 36, 'test message')
    alarm1.set_countdown(10, 'test message')

    alarm1.set_alarm(23, 35, 'test message')
    alarm1.set_countdown(11, 'test message')

    # 啟動鬧鐘
    await asyncio.gather(
        alarm1.loop(),
        alarm2.loop()
    )

if __name__ == '__main__':
    # 運行主函數
    asyncio.run(main())