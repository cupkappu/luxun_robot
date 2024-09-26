import asyncio
import time

class AsyncAlarm:
    def __init__(self, user):
        self.user = user
        self.alarms = []
        self.countdowns = []

    async def set_alarm(self, hour, minute, callback):
        print(f'Add alarm {hour}:{minute}')
        self.alarms.append((hour, minute, callback))

    async def set_countdown(self, seconds, callback):
        print(f'Add countdown {seconds}s')
        self.countdowns.append((seconds, callback))

    async def check_alarm(self):
        while True:
            current_time = time.localtime()
            for alarm in self.alarms:
                if current_time.tm_hour == alarm[0] and current_time.tm_min == alarm[1]:
                    alarm[2](self.user)
                    self.alarms.remove(alarm)
            await asyncio.sleep(1)

    async def check_countdown(self):
        while self.countdowns:
            for i in range(len(self.countdowns)):
                remaining_time = self.countdowns[i][0]
                if remaining_time <= 0:
                    self.countdowns[i][1](self.user)
                    self.countdowns.remove(self.countdowns[i])
                else:
                    self.countdowns[i] = (remaining_time - 1, self.countdowns[i][1])
            await asyncio.sleep(1)  # 每秒更新一次倒計時

    async def loop(self):
        await asyncio.gather(
            self.check_alarm(),
            self.check_countdown()
        )

# 回調函數示例
def alarm_callback(user):
    print(f"鬧鐘響了! 使用者: {user}")

def countdown_callback(user):
    print(f"倒計時結束! 使用者: {user}")

# 使用示例
async def main():
    # 為兩個不同用戶創建鬧鐘實例
    alarm1 = AsyncAlarm("用戶1")
    alarm2 = AsyncAlarm("用戶2")

    # 設置鬧鐘和倒計時
    await alarm1.set_alarm(0, 28, alarm_callback)  # 設置14:30的鬧鐘
    await alarm1.set_countdown(10, countdown_callback)  # 設置10秒的倒計時

    await alarm2.set_alarm(0, 27, alarm_callback)  # 設置15:00的鬧鐘
    await alarm2.set_countdown(20, countdown_callback)  # 設置20秒的倒計時

    # 啟動鬧鐘
    await asyncio.gather(
        alarm1.loop(),
        alarm2.loop()
    )

if __name__ == '__main__':
    # 運行主函數
    asyncio.run(main())