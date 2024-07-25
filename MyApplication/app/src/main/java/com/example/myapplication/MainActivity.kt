package com.example.myapplication

import android.annotation.SuppressLint
import android.net.http.SslError
import android.os.Bundle
import android.util.Log
import android.view.ViewGroup
import android.webkit.HttpAuthHandler
import android.webkit.SafeBrowsingResponse
import android.webkit.SslErrorHandler
import android.webkit.WebResourceError
import android.webkit.WebResourceRequest
import android.webkit.WebResourceResponse
import android.webkit.WebSettings
import android.webkit.WebView
import android.webkit.WebViewClient
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.text.KeyboardActions
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.TextField
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.input.ImeAction
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.viewinterop.AndroidView
import androidx.webkit.WebViewClientCompat
import com.appmattus.certificatetransparency.installCertificateTransparencyProvider
import com.example.myapplication.ui.theme.MyApplicationTheme


class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        installCertificateTransparencyProvider {

            +"*"
            failOnError = false
        }
        setContent {
            MyApplicationTheme {
                // A surface container using the 'background' color from the theme
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = MaterialTheme.colorScheme.background
                ) {
                    Greeting()
                }
            }
        }
    }
}

class MyWebClient : WebViewClient() {
    override fun shouldOverrideUrlLoading(view: WebView?, request: WebResourceRequest): Boolean {
        Log.d("wv", "shouldOverrideUrlLoading ${request.url}")
        return false
    }

    override fun onReceivedError(
        view: WebView?,
        request: WebResourceRequest,
        error: WebResourceError
    ) {
        Log.d("wv", "onReceivedError ${error.errorCode} ${error.description} ${request.url}")
    }

    override fun onReceivedHttpAuthRequest(
        view: WebView?,
        handler: HttpAuthHandler, host: String?, realm: String?
    ) {
        Log.d("wv", "onReceivedHttpAuthRequest $host $realm")
    }

    override fun onReceivedHttpError(
        view: WebView?, request: WebResourceRequest?, errorResponse: WebResourceResponse?
    ) {
        Log.d("wv", "onReceivedHttpError ${request?.url} $errorResponse")
    }

    override fun onReceivedLoginRequest(
        view: WebView?, realm: String?,
        account: String?, args: String?
    ) {
        Log.d("wv", "onReceivedLoginRequest $realm $account")
    }

    @SuppressLint("WebViewClientOnReceivedSslError")
    override fun onReceivedSslError(
        view: WebView?, handler: SslErrorHandler,
        error: SslError?
    ) {
        Log.d("wv", "onReceivedSslError $error")
        handler.proceed()
    }

}

@SuppressLint("SetJavaScriptEnabled")
@Composable
fun Greeting() {
    var url by rememberSaveable {
        mutableStateOf("Hi, my name is a law")
    }
    var urlEd by rememberSaveable {
        mutableStateOf("https://roskazna.gov.ru/")
    }
    var webView: WebView? = null
    Column {
        Text(
            text = url,
        )
        TextField(
            value = urlEd,
            onValueChange = { urlEd = it },
            singleLine = true,
            keyboardOptions = KeyboardOptions(imeAction = ImeAction.Done),
            keyboardActions = KeyboardActions(onDone = {
                url = urlEd
                webView?.loadUrl(url)
            })
        )
        Box(modifier = Modifier.fillMaxSize()) {
            AndroidView(
                factory = {
                    WebView.setWebContentsDebuggingEnabled(true)
                    val w = WebView(it).apply {
                        layoutParams = ViewGroup.LayoutParams(
                            ViewGroup.LayoutParams.MATCH_PARENT,
                            ViewGroup.LayoutParams.MATCH_PARENT
                        )
                    }
                    w.webViewClient = MyWebClient()
                    w.settings.mixedContentMode = WebSettings.MIXED_CONTENT_ALWAYS_ALLOW
                    w.settings.javaScriptEnabled = true
                    w.settings.domStorageEnabled = true
                    w.settings.useWideViewPort = true
                    // val HTMLstring =
                    //     "<!DOCTYPE html><html><head><style>html, body { margin: 0; padding: 0; height: 100%; }</style></head><body><div style='height: 100%; background-color: green;'></div></body><html>"
                    // it.loadDataWithBaseURL(null, HTMLstring, "text/html", "utf-8", null)
                    // it.loadUrl("http://lib.ru/")
                    //w.loadUrl("https://roskazna.gov.ru/")
                    w.loadUrl("https://10.5.29.158:8087/?termnum=1&username=KRASN_MO&password=1")
                    //w.loadUrl("https://ccmmp.magnit.ru/")
                    w
                },
                update = {
                    webView = it
                },
            )
        }
    }

}

@Preview(showBackground = true)
@Composable
fun GreetingPreview() {
    MyApplicationTheme {
        Greeting()
    }
}