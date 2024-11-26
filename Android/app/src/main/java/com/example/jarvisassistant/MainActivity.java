package com.example.jarvisassistant;

import android.animation.ObjectAnimator;
import android.content.Intent;
import android.os.Bundle;
import android.speech.RecognizerIntent;
import android.speech.tts.TextToSpeech;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.TextView;
import android.widget.Toast;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.content.ContextCompat;
import com.chaquo.python.PyObject;
import com.chaquo.python.Python;
import com.chaquo.python.android.AndroidPlatform;
import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
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
    private static final String PYTHON_SCRIPTS_DIR = "python_scripts";
    private PyObject inputProcessor;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        initViews();
        setupListeners();
        initTextToSpeech();
        initPython();
        loadPythonScripts();
    }

    private void initViews() {
        inputText = findViewById(R.id.inputText);
        sendButton = findViewById(R.id.sendButton);
        voiceButton = findViewById(R.id.voiceButton);
        menuButton = findViewById(R.id.menuButton);
        chatView = findViewById(R.id.chatView);
        pythonCodeView = findViewById(R.id.pythonCodeView);
    }

    private void setupListeners() {
        sendButton.setOnClickListener(v -> {
            animateButton(sendButton);
            String message = inputText.getText().toString();
            if (!message.isEmpty()) {
                sendMessage(message);
            }
        });

        voiceButton.setOnClickListener(v -> {
            animateButton(voiceButton);
            speak();
        });

        menuButton.setOnClickListener(v -> {
            animateButton(menuButton);
            showPythonScripts();
        });
    }

    private void initTextToSpeech() {
        tts = new TextToSpeech(this, status -> {
            if (status == TextToSpeech.SUCCESS) {
                int result = tts.setLanguage(Locale.CHINESE);
                if (result == TextToSpeech.LANG_MISSING_DATA || result == TextToSpeech.LANG_NOT_SUPPORTED) {
                    Toast.makeText(this, "语言不支持", Toast.LENGTH_SHORT).show();
                }
            } else {
                Toast.makeText(this, "TTS初始化失败", Toast.LENGTH_SHORT).show();
            }
        });
    }

    private void initPython() {
        if (!Python.isStarted()) {
            Python.start(new AndroidPlatform(this));
        }
        Python py = Python.getInstance();
        PyObject module = py.getModule("jarvis.InputProcessor");
        inputProcessor = module.callAttr("InputProcessor");
    }

    private void loadPythonScripts() {
        File scriptsDir = new File(getFilesDir(), PYTHON_SCRIPTS_DIR);
        if (!scriptsDir.exists()) {
            scriptsDir.mkdirs();
        }

        File[] scriptFiles = scriptsDir.listFiles((dir, name) -> name.endsWith(".py"));
        if (scriptFiles != null) {
            for (File scriptFile : scriptFiles) {
                try {
                    String scriptContent = readFile(scriptFile);
                    String scriptName = scriptFile.getName().replace(".py", "");
                    Python.getInstance().getModule("builtins").callAttr("exec", scriptContent);
                } catch (IOException e) {
                    e.printStackTrace();
                }
            }
        }
    }

    private void sendMessage(String message) {
        chatView.append("You: " + message + "\n");
        inputText.setText("");

        PyObject response = inputProcessor.callAttr("process_input", message);
        String responseStr = response.toString();
        chatView.append("Jarvis: " + responseStr + "\n");
        tts.speak(responseStr, TextToSpeech.QUEUE_FLUSH, null, null);
    }

    private void speak() {
        Intent intent = new Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH);
        intent.putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM);
        intent.putExtra(RecognizerIntent.EXTRA_LANGUAGE, Locale.CHINESE);
        intent.putExtra(RecognizerIntent.EXTRA_PROMPT, "请说话...");
        try {
            startActivityForResult(intent, REQUEST_CODE_SPEECH_INPUT);
        } catch (Exception e) {
            Toast.makeText(this, "语音识别不可用", Toast.LENGTH_SHORT).show();
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

    private void showPythonScripts() {
        StringBuilder scriptList = new StringBuilder("可用的Python脚本:\n\n");
        File scriptsDir = new File(getFilesDir(), PYTHON_SCRIPTS_DIR);
        File[] scriptFiles = scriptsDir.listFiles((dir, name) -> name.endsWith(".py"));

        if (scriptFiles != null) {
            for (int i = 0; i < scriptFiles.length; i++) {
                String scriptName = scriptFiles[i].getName().replace(".py", "");
                scriptList.append(i + 1).append(". ").append(scriptName).append("\n");
            }
        }

        scriptList.append("\n输入脚本名称来运行脚本。");
        pythonCodeView.setText(scriptList.toString());
        pythonCodeView.setVisibility(View.VISIBLE);
    }

    private void animateButton(Button button) {
        ObjectAnimator scaleDown = ObjectAnimator.ofFloat(button, "scaleX", 0.7f);
        scaleDown.setDuration(100);
        scaleDown.setRepeatCount(1);
        scaleDown.setRepeatMode(ObjectAnimator.REVERSE);
        scaleDown.start();

        ObjectAnimator scaleUp = ObjectAnimator.ofFloat(button, "scaleY", 0.7f);
        scaleUp.setDuration(100);
        scaleUp.setRepeatCount(1);
        scaleUp.setRepeatMode(ObjectAnimator.REVERSE);
        scaleUp.start();

        button.setBackgroundTintList(ContextCompat.getColorStateList(this, R.color.button_pressed));
        button.postDelayed(() -> button.setBackgroundTintList(ContextCompat.getColorStateList(this, R.color.button_normal)), 200);
    }

    private String readFile(File file) throws IOException {
        byte[] encoded = new byte[(int) file.length()];
        try (FileInputStream fis = new FileInputStream(file)) {
            fis.read(encoded);
        }
        return new String(encoded, StandardCharsets.UTF_8);
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

