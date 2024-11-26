from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/python-code', methods=['GET'])
def get_python_code():
    code = """
def fibonacci(n):
    if n <= 1:
        return n
    else:
        return fibonacci(n-1) + fibonacci(n-2)

def main():
    num = 10
    print(f"第 {num} 个斐波那契数是: {fibonacci(num)}")

if __name__ == "__main__":
    main()
    """
    return jsonify({"code": code})

if __name__ == '__main__':
    app.run(port=8000)
    """

</ReactProject>

现在,让我们更新Android版本的代码:

<ReactProject id="jarvis-assistant">

首先,我们需要更新`MainActivity.java`文件:

```java file="android/MainActivity.java" type="code"
package com.example.jarvisassistant;

import android.os.Bundle;
import android.speech.RecognizerIntent;
import android.speech.tts.TextToSpeech;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.TextView;
import androidx.appcompat.app.AppCompatActivity;
import java.util.ArrayList;
import java.util.Locale;

public class MainActivity extends AppCompatActivity {
    private EditText inputText;
    private Button sendButton;
    private Button voiceButton;
    private Button menuButton;
    private TextView chatView;
    private TextView pythonCodeView;
    private TextToSpeech tts;
    private static final int REQUEST_CODE_SPEECH_INPUT = 1000;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        inputText = findViewById(R.id.inputText);
        sendButton = findViewById(R.id.sendButton);
        voiceButton = findViewById(R.id.voiceButton);
        menuButton = findViewById(R.id.menuButton);
        chatView = findViewById(R.id.chatView);
        pythonCodeView = findViewById(R.id.pythonCodeView);

        sendButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                String message = inputText.getText().toString();
                if (!message.isEmpty()) {
                    sendMessage(message);
                }
            }
        });

        voiceButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                speak();
            }
        });

        menuButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                showPythonCode();
            }
        });

        tts = new TextToSpeech(this, new TextToSpeech.OnInitListener() {
            @Override
            public void onInit(int status) {
                if (status == TextToSpeech.SUCCESS) {
                    int result = tts.setLanguage(Locale.CHINESE);
                    if (result == TextToSpeech.LANG_MISSING_DATA || result == TextToSpeech.LANG_NOT_SUPPORTED) {
                        // 语言数据丢失或不支持
                    }
                } else {
                    // TTS初始化失败
                }
            }
        });
    }

    private void sendMessage(String message) {
        chatView.append("You: " + message + "\n");
        inputText.setText("");

        String response = getResponseFromBackend(message);
        chatView.append("Jarvis: " + response + "\n");
        tts.speak(response, TextToSpeech.QUEUE_FLUSH, null, null);
    }

    private void speak() {
        Intent intent = new Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH);
        intent.putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM);
        intent.putExtra(RecognizerIntent.EXTRA_LANGUAGE, Locale.CHINESE);
        intent.putExtra(RecognizerIntent.EXTRA_PROMPT, "请说话...");
        try {
            startActivityForResult(intent, REQUEST_CODE_SPEECH_INPUT);
        } catch (Exception e) {
            // 处理错误
        }
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);

        if (requestCode == REQUEST_CODE_SPEECH_INPUT) {
            if (resultCode == RESULT_OK && data != null) {
                ArrayList<String> result = data.getStringArrayListExtra(RecognizerIntent.EXTRA_RESULTS);
                String spokenText = result.get(0);
                inputText.setText(spokenText);
                sendMessage(spokenText);
            }
        }
    }

    private String getResponseFromBackend(String message) {
        return JarvisBackend.processCommand(message);
    }

    private void showPythonCode() {
        String pythonCode = "def fibonacci(n):\n" +
                "    if n <= 1:\n" +
                "        return n\n" +
                "    else:\n" +
                "        return fibonacci(n-1) + fibonacci(n-2)\n\n" +
                "def main():\n" +
                "    num = 10\n" +
                "    print(f\"第 {num} 个斐波那契数是: {fibonacci(num)}\")\n\n" +
                "if __name__ == \"__main__\":\n" +
                "    main()";
        pythonCodeView.setText(pythonCode);
        pythonCodeView.setVisibility(View.VISIBLE);
    }

    @Override
    protected void onDestroy() {
        if (tts != null) {
            tts.stop();
            tts.shutdown();
        }
        super.onDestroy();
    }
}

