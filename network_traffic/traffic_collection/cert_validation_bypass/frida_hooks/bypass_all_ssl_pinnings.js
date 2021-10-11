/* =========================================================================================================  

    This is a Frida script that performs SSL certificate pinning bypass for both Android Java/JVM and Unity.
    This script should be called using the bypass_all_ssl_pinnings.sh script.

=========================================================================================================  */


/* ===================================================================================

    PART 1: The following performs SSL pinning bypass for Unity.

=================================================================================== */
const libunity = 'libunity.so';
const hooked_function = 'mbedtls_x509_crt_verify_with_profile';
// This function_offset is a placeholder to be replaced by a real address.
const function_offset = 0x0;

// Function that hooks to mbedtls_x509_crt_verify_with_profile and performs the SSL pinning bypass.
function SSLPinningBypassCallback(funcName) {
    this.funcName = funcName;
    
    this.onEnter = function (args) {
        console.log("[.] onEnter: " + hooked_function);
        this.flags = args[5];
    };
    
    this.onLeave = function (retval) {
        console.log("[.] onLeave: " + hooked_function);
        console.log("[+] Replacing return value " + retval + " with 0x0...");
        retval.replace(0x0);
        console.log("[+] Replacing flag value " + this.flags.readPointer() + " with 0x0 (at address " + this.flags + ")...");
        Memory.writeU32(this.flags, 0x0);
        console.log("\n\n");
    };
};

// Function that waits for libunity.so to load. 
// It then attaches the SSLPinningBypassCallback function to the address of mbedtls_x509_crt_verify_with_profile.
function bypassUnitySSLPinning(arg) {
    var delay = 10; // Delay and contend for CPU.
    var intervalPointer = setInterval(function() {
        var modulesArray = Process.enumerateModules();
        for(var i=0; i<modulesArray.length; i++) {
            if(modulesArray[i].path.indexOf(libunity)!=-1) {
                var base_address = Module.findBaseAddress(libunity);
                var function_address = base_address.add(function_offset); // Spatial for function mbedtls_x509_crt_verify_with_profile
                clearInterval(intervalPointer);
                console.log("[+] Attempting to hook " + hooked_function);
                Interceptor.attach(function_address, new SSLPinningBypassCallback(libunity + ":" + hooked_function));
                console.log("[+] Done hook " + hooked_function);

            }
        }  
    }, delay);
    console.log("[I] Attempting to bypass Unity SSL pinning...");
    console.log("[+] Attached to libunity.so...");
    console.log("[+] Waiting...");
}

/* ===================================================================================

    PART 2: The following performs SSL pinning bypass for Unreal.

=================================================================================== */
const libunreal = 'libUE4.so';
const verifyCertFunction = 'X509_verify_cert';
// We have 2 offsets depending on the version of the OpenSSL used in Unreal Engine
// See: https://github.uci.edu/NetworkingGroup/vr-project/issues/21#issuecomment-908
const offset1 = 23;
const offset2 = 25;
const errorCodeOffset1 = Process.pointerSize * offset1;
const errorCodeOffset2 = Process.pointerSize * offset2;

function X509Callback(funcName) {
    this.funcName = funcName;
    
    this.onEnter = function (args) {
        console.log("[.] onEnter: " + verifyCertFunction);
        this.ctx = args[0];
    };
    
    this.onLeave = function (retval) {
        console.log("[.] onLeave: " + verifyCertFunction);
        var structPtr = this.ctx;
        if (retval == 0x0) {
            console.log("[+] Replacing return value " + retval + " with 0x1...");
            retval.replace(0x1);
            console.log("[+] Clearing error code because of self-signed certificate...");
            if (structPtr.add(errorCodeOffset1).readInt() == 19) {
                console.log("[+] Error code 19 for self-signed certificate found at position " + offset1 + "...");
                structPtr.add(errorCodeOffset1).writeInt(0);
            }
            else if (structPtr.add(errorCodeOffset2).readInt() == 19) {
                console.log("[+] Error code 19 for self-signed certificate found at position " + offset2 + "...");
                structPtr.add(errorCodeOffset2).writeInt(0);
            } else {
                console.log("[I] NOT attempting to bypass Unreal SSL pinning...");
                console.log("[I] Self-signed certificate error code is not found in the struct...");
            }
            console.log("\n\n");
        }
    };
};

function bypassUnrealSSLPinning() {
    var delay = 10; // Fight for CPU
    var intervalPointer = setInterval(function() {
        var modulesArray = Process.enumerateModules();
        for(var i=0; i<modulesArray.length; i++) {
            if(modulesArray[i].path.indexOf(libunreal)!=-1) {
                var base_address = Module.findBaseAddress(libunreal);
                clearInterval(intervalPointer);
                Interceptor.attach(Module.findExportByName(libunreal, verifyCertFunction), new X509Callback(libunreal + ":" + 'X509_verify_cert function'));
            }
        }  
    }, delay);
    console.log("[I] Attempting to bypass Unreal SSL pinning...");
    console.log("[+] Attached to libUE4.so...");
    console.log("[+] Waiting...");
}


/* ===================================================================================

    PART 3: The following performs SSL pinning bypass for Android Java/JVM.
    Source: https://codeshare.frida.re/@masbog/frida-android-unpinning-ssl/

=================================================================================== */
function bypassJavaSSLPinning() {
    setTimeout(function() {
        Java.perform(function() {
            console.log("");
            console.log("[.] Android Cert Pinning Bypass");

            var CertificateFactory = Java.use("java.security.cert.CertificateFactory");
            var FileInputStream = Java.use("java.io.FileInputStream");
            var BufferedInputStream = Java.use("java.io.BufferedInputStream");
            var X509Certificate = Java.use("java.security.cert.X509Certificate");
            var KeyStore = Java.use("java.security.KeyStore");
            var TrustManagerFactory = Java.use("javax.net.ssl.TrustManagerFactory");
            var SSLContext = Java.use("javax.net.ssl.SSLContext");
            var X509TrustManager = Java.use('javax.net.ssl.X509TrustManager');
            //var is_android_n = 0;

            //--------
            console.log("[.] TrustManagerImpl Android 7+ detection...");
            // Android 7+ TrustManagerImpl
            // The work in the following NCC blogpost was a great help for this hook!
            // hattip @AdriVillaB :)
            // https://www.nccgroup.trust/uk/about-us/newsroom-and-events/blogs/2017/november/bypassing-androids-network-security-configuration/
            // See also: https://codeshare.frida.re/@avltree9798/universal-android-ssl-pinning-bypass/
            try {
                var TrustManagerImpl = Java.use('com.android.org.conscrypt.TrustManagerImpl');
                var ArrayList = Java.use("java.util.ArrayList");
                TrustManagerImpl.verifyChain.implementation = function(untrustedChain, trustAnchorChain,
                    host, clientAuth, ocspData, tlsSctData) {
                    console.log("[+] Bypassing TrustManagerImpl->verifyChain()");
                    return untrustedChain;
                }
                TrustManagerImpl.checkTrustedRecursive.implementation = function(certs, host, clientAuth, untrustedChain,
                    trustAnchorChain, used) {
                    console.log("[+] Bypassing TrustManagerImpl->checkTrustedRecursive()");
                    return ArrayList.$new();
                };
            } catch (err) {
                console.log("[-] TrustManagerImpl Not Found");
            }


            //if (is_android_n === 0) {
            //--------
            console.log("[.] TrustManager Android < 7 detection...");
            // Implement a new TrustManager
            // ref: https://gist.github.com/oleavr/3ca67a173ff7d207c6b8c3b0ca65a9d8
            var TrustManager = Java.registerClass({
                name: 'com.sensepost.test.TrustManager',
                implements: [X509TrustManager],
                methods: {
                    checkClientTrusted: function(chain, authType) {},
                    checkServerTrusted: function(chain, authType) {},
                    getAcceptedIssuers: function() {
                        return [];
                    }
                }
            });

            // Prepare the TrustManagers array to pass to SSLContext.init()
            var TrustManagers = [TrustManager.$new()];

            // Get a handle on the init() on the SSLContext class
            var SSLContext_init = SSLContext.init.overload(
                '[Ljavax.net.ssl.KeyManager;', '[Ljavax.net.ssl.TrustManager;', 'java.security.SecureRandom');

            try {
                // Override the init method, specifying our new TrustManager
                SSLContext_init.implementation = function(keyManager, trustManager, secureRandom) {
                    console.log("[+] Overriding SSLContext.init() with the custom TrustManager android < 7");
                    SSLContext_init.call(this, keyManager, TrustManagers, secureRandom);
                };
            } catch (err) {
                console.log("[-] TrustManager Not Found");
            }
            //}

            //-------
            console.log("[.] OkHTTP 3.x detection...");
            // OkHTTP v3.x
            // Wrap the logic in a try/catch as not all applications will have
            // okhttp as part of the app.
            try {
                var CertificatePinner = Java.use('okhttp3.CertificatePinner');
                console.log("[+] OkHTTP 3.x Found");
                CertificatePinner.check.overload('java.lang.String', 'java.util.List').implementation = function() {
                    console.log("[+] OkHTTP 3.x check() called. Not throwing an exception.");
                };
            } catch (err) {
                // If we dont have a ClassNotFoundException exception, raise the
                // problem encountered.
                console.log("[-] OkHTTP 3.x Not Found")
            }

            //--------
            console.log("[.] Appcelerator Titanium detection...");
            // Appcelerator Titanium PinningTrustManager
            // Wrap the logic in a try/catch as not all applications will have
            // appcelerator as part of the app.
            try {
                var PinningTrustManager = Java.use('appcelerator.https.PinningTrustManager');
                console.log("[+] Appcelerator Titanium Found");
                PinningTrustManager.checkServerTrusted.implementation = function() {
                    console.log("[+] Appcelerator checkServerTrusted() called. Not throwing an exception.");
                }

            } catch (err) {
                // If we dont have a ClassNotFoundException exception, raise the
                // problem encountered.
                console.log("[-] Appcelerator Titanium Not Found");
            }

        });
    }, 0);
}

// Main
function main() {
    bypassJavaSSLPinning();
    if (function_offset == 0x0) {
        console.log("[I] Not attempting to bypass Unity or Unreal SSL pinning since this APK belongs to other categories...\n");
    } else {
        console.log("[I] Attempting to bypass Unity or Unreal SSL pinning...\n");
        if (function_offset == 0x1) {
            bypassUnrealSSLPinning();
        } else  {
            bypassUnitySSLPinning();
        }
    }
}

main();