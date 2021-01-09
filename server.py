import asyncio
import json
import os
import traceback

from slack_sdk.webhook.async_client import AsyncWebhookClient

slack = AsyncWebhookClient(url=os.environ['SLACK_WEBHOOK_URL'])


async def process_record(record):
    message = json.loads(record['message'])
    color = {
        'ERROR': 'danger',
        'WARNING': 'warning',
    }.get(message['levelname'])

    if color:
        await slack.send(
            text=message['message'],
            attachments=[{
                'color': color,
                'fields': [
                    {
                        'title': k,
                        'value': v,
                        'short': k not in {'exc_info'},
                    }
                    for k, v in {
                        'app': record['kubernetes']['labels']['app'],
                        'namespace_name': record['kubernetes']['namespace_name'],
                        'name': message['name'],
                        'lineno': message['lineno'],
                        'funcName': message['funcName'],
                        'levelname': message['levelname'],
                        'exc_info': message.get('exc_info'),
                    }.items()
                ],
            }]
        )


async def handle(reader, writer):
    try:
        while True:
            line = await reader.readline()

            if not line:
                break

            try:
                record = json.loads(line)
            except json.decoder.JSONDecodeError:
                break

            try:
                await process_record(record)
            except (KeyError, json.decoder.JSONDecodeError):
                pass
            except Exception:
                traceback.print_exc()
    except Exception:
        traceback.print_exc()
    finally:
        writer.close()


async def main():
    server = await asyncio.start_server(handle, '0.0.0.0', 5170)

    addr = server.sockets[0].getsockname()
    print(f'Serving on {addr}')

    async with server:
        await server.serve_forever()


if __name__ == '__main__':
    asyncio.run(main())
