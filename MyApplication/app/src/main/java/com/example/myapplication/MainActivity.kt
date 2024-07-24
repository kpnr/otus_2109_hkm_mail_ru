package com.example.myapplication

import android.annotation.SuppressLint
import android.graphics.Bitmap
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
import com.example.myapplication.ui.theme.MyApplicationTheme
import java.net.URL
import javax.net.ssl.HttpsURLConnection


class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
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

    override fun onPageStarted(view: WebView?, url: String?, favicon: Bitmap?) {
        Log.d("wv", "onPageStarted $url")
    }

    override fun onLoadResource(view: WebView?, url: String?) {
        Log.d("wv", "onLoadResource $url")
    }

    override fun shouldInterceptRequest(
        view: WebView?,
        request: WebResourceRequest?
    ): WebResourceResponse? {
        Log.d("wv", "shouldInterceptRequest ${request?.url}")
//        if (request == null || request.method != "GET" || request.url.scheme != "https") return null
//        val conn = URL(request.url.toString()).openConnection()
//        if (conn !is HttpsURLConnection) return null
//        for ((k, v) in request.requestHeaders) {
//            conn.setRequestProperty(k, v)
//        }
//        conn.allowUserInteraction = false
//        conn.connectTimeout = 3000
//        conn.readTimeout = 300_000
//        conn.doInput = true
//        conn.doOutput = false
//        conn.connect()
//        val respCode = conn.responseCode
//        if(respCode != 200) return null
//        val respHdrs: MutableMap<String, String> = mutableMapOf()
//        for ((k: String?, v) in conn.headerFields.entries) {
//            if(k !is String) continue
//            respHdrs[k] = v[0]
//        }
//        return WebResourceResponse(
//            conn.contentType,
//            conn.contentEncoding,
//            respCode,
//            conn.responseMessage,
//            respHdrs,
//            conn.inputStream
//        )
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

    override fun onSafeBrowsingHit(
        view: WebView?, request: WebResourceRequest?,
        @WebViewClientCompat.SafeBrowsingThreat threatType: Int, callback: SafeBrowsingResponse
    ) {
        Log.d("wv", "onSafeBrowsingHit ${request?.url}")
        callback.proceed(false)
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
                    w.settings.safeBrowsingEnabled = false
                    w.settings.domStorageEnabled = true
                    w.settings.useWideViewPort = true
                    // val HTMLstring =
                    //     "<!DOCTYPE html><html><head><style>html, body { margin: 0; padding: 0; height: 100%; }</style></head><body><div style='height: 100%; background-color: green;'></div></body><html>"
                    // it.loadDataWithBaseURL(null, HTMLstring, "text/html", "utf-8", null)
                    // it.loadUrl("http://lib.ru/")
                    // it.loadUrl("https://roskazna.gov.ru/")
                    //w.loadUrl("https://10.5.29.158:8087/")
                    w.loadUrl("https://ccmmp.magnit.ru/")
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