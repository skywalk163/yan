const { spawn } = require('child_process');
const path = require('path');

function activate(context) {
    const debugServer = vscode.debug.createDebugAdapterServer({
        port: 0,
        host: 'localhost'
    });

    context.subscriptions.push(debugServer);

    const factory = {
        createDebugAdapterSession() {
            return new YanDebugAdapter();
        },
        dispose() {}
    };

    vscode.debug.registerDebugAdapterSessionFactory(factory);
}

class YanDebugAdapter {
    constructor() {
        this.process = null;
        this.callbacks = {};
        this.seq = 0;
    }

    start() {
        const yanPath = path.join(__dirname, '..', 'yan', 'main.py');
        this.process = spawn('python', [yanPath, '--debug'], {
            stdio: ['pipe', 'pipe', 'pipe']
        });

        this.process.stdout.on('data', (data) => {
            this.handleOutput(data.toString());
        });

        this.process.stderr.on('data', (data) => {
            console.error(data.toString());
        });
    }

    handleOutput(data) {
        try {
            const response = JSON.parse(data);
            if (response.seq && this.callbacks[response.seq]) {
                this.callbacks[response.seq](response);
                delete this.callbacks[response.seq];
            }
        } catch (e) {
            console.error('Failed to parse debug output:', e);
        }
    }

    sendCommand(command) {
        return new Promise((resolve, reject) => {
            const seq = ++this.seq;
            command.seq = seq;
            this.callbacks[seq] = resolve;
            this.process.stdin.write(JSON.stringify(command) + '\n');

            setTimeout(() => {
                if (this.callbacks[seq]) {
                    reject(new Error('Debug command timeout'));
                    delete this.callbacks[seq];
                }
            }, 5000);
        });
    }

    disconnect() {
        if (this.process) {
            this.process.kill();
            this.process = null;
        }
    }
}

module.exports = { activate };
