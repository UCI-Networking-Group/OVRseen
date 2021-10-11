# OVRseen License

## OVRseen

OVRseen is dual-licensed under the [MIT License](https://opensource.org/licenses/MIT) and the [GNU General Public License version 3 (GPLv3)](https://www.gnu.org/licenses/gpl-3.0.en.html). You can find a copy of the MIT License in the file `COPYING-MIT.txt`, and a copy of the GPLv3 in the file `COPYING-GPL3.txt`.

The following parts of OVRseen are covered by GPLv3:

- `network_traffic/post-processing/pii_helper.py`
- `network_traffic/post-processing/json_keys.py`
- `network_traffic/post-processing/extract_from_tshark.py`
- `network_traffic/post-processing/utils/utils.py`
- `privacy_policy/network-to-policy_consistency/Preprocessor.py`
- `privacy_policy/network-to-policy_consistency/lib/UnicodeNormalizer.py`
- `privacy_policy/purpose_extraction/process-polisis-analysis-json.py`
- `network_traffic/post-processing/filter_lists/piholeblocklist_default_smarttv_abp.txt`

If those parts get used, GPLv3 applies to all of OVRseen. Otherwise, you may modify and/or redistribute OVRseen under either the MIT License or GPLv3.

## Third Party Notice

OVRseen incorporates materials from the third-party projects listed below.

### PoliCheck

The following files are based on [PoliCheck](https://github.com/benandow/PrivacyPolicyAnalysis):

- `privacy_policy/network-to-policy_consistency/ConsistencyAnalysis.py`
- `privacy_policy/network-to-policy_consistency/DisclosureClassification.py`
- `privacy_policy/network-to-policy_consistency/PatternExtractionNotebook.py`
- `privacy_policy/network-to-policy_consistency/RemoveSameSentenceContradictions.py`
- `privacy_policy/network-to-policy_consistency/extra_training_data.txt`
- `privacy_policy/network-to-policy_consistency/lib/ConsistencyDatabase.py`
- `privacy_policy/network-to-policy_consistency/lib/Consistency.py`
- `privacy_policy/network-to-policy_consistency/lib/ExclusionDetector.py`
- `privacy_policy/network-to-policy_consistency/lib/OntologyOps.py`
- `privacy_policy/network-to-policy_consistency/lib/TermPreprocessor2.py`

We are licensed to modify and redistribute the original code under the following terms:

> Copyright (c) 2019, North Carolina State University
> All rights reserved.
>
> Redistribution and use in source and binary forms, with or without modification, are permitted provided
> that the following conditions are met:
>
> 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
>
> 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
>
> 3. The names “North Carolina State University”, “NCSU” and any trade‐name, personal name, trademark, trade device, service mark, symbol, image, icon, or any abbreviation, contraction or simulation thereof owned by North Carolina State University must not be used to endorse or promote products derived from this software without prior written permission.
>
> THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

### HtmlToPlaintext

The following files are based on [HtmlToPlaintext](https://github.com/benandow/HtmlToPlaintext) -- PoliCheck's HTML preprocessor:

- `privacy_policy/network-to-policy_consistency/Preprocessor.py`
- `privacy_policy/network-to-policy_consistency/lib/UnicodeNormalizer.py`

We are licensed to modify and redistribute the original code under the GPLv3. You can find a copy of the GPLv3 in the file `COPYING-GPL3.txt`.

### AppMon

The following file is based on [AppMon](https://github.com/dpnishant/appmon):

- `network_traffic/traffic_collection/apk_processing/apk_builder.py`

We are licensed to modify and redistribute the original code under the [Apache License version 2.0](https://www.apache.org/licenses/LICENSE-2.0).
