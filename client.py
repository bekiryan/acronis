import asyncio


class Client(asyncio.Protocol):
    def __init__(self, message, on_con_lost):
        self.exception = None
        self.data = None
        self.message = message
        self.on_con_lost = on_con_lost

    def connection_made(self, transport):
        self.validate_message(self.message)
        transport.write(self.message.encode())

    def data_received(self, data):
        self.validate_result(data)
        self.data = int(data.decode())

    def connection_lost(self, exc):
        self.on_con_lost.set_result(True)

    def validate_message(self, message):
        try:
            message = [value.strip() for value in message.split(',')]
            if len(message) != 2:
                raise ValueError('Message must have 2 values separated by a comma')
            for value in message:
                if not value.isdigit():
                    raise ValueError('Message values must be positive integers')
                elif not int(value) <= 100:
                    raise ValueError('Message values must be less than 100')

        except ValueError as e:
            self.exception = str(e)

    def validate_result(self, data):
        try:
            int(data.decode())
        except ValueError as e:
            self.exception = data.decode()


async def run_client(num1, num2):
    loop = asyncio.get_running_loop()

    on_con_lost = loop.create_future()
    message = '{}, {}'.format(num1, num2)

    transport, protocol = await loop.create_connection(
        lambda: Client(message, on_con_lost),
        '127.0.0.1', 8888)
    if protocol.exception:
        transport.close()
        raise ValueError(protocol.exception)
    try:
        await on_con_lost
    finally:
        if protocol.exception:
            raise ValueError(protocol.exception)
        result = protocol.data
        transport.close()
        return result


if __name__ == '__main__':
    num1 = 10
    num2 = 20
    result = asyncio.run(run_client(num1, num2))
    print(f"Sum of {num1} and {num2} is {result}")
