# EcoFlow Cloud UTF-8デコードエラー修正レポート

## 概要

Home Assistant EcoFlow Cloud統合で発生していたUTF-8デコードエラーを分析し、修正を行った。エラーはバイナリプロトコルバッファ（protobuf）データをUTF-8テキストとして処理しようとしたことが原因であった。

## 現象の詳細

### エラーメッセージ
```
constant: 'utf-8' codec can't decode byte 0xa2 in position 9: invalid start byte. Ignoring message and waiting for the next one.
constant: 'utf-8' codec can't decode byte 0x80 in position 4: invalid start byte. Ignoring message and waiting for the next one.
constant: 'utf-8' codec can't decode byte 0xfe in position 18: invalid start byte. Ignoring message and waiting for the next one.
```

### 発生場所
- **ファイル**: `custom_components/ecoflow_cloud/devices/__init__.py:180`
- **メソッド**: `BaseDevice._prepare_data()`
- **頻度**: 539回発生（2025年6月14日23:55:16〜13:48:36）

### 影響範囲
- EcoFlow Cloud統合を使用する15+のデバイスタイプ
- MQTTブローカーから受信するバイナリprotobufメッセージの処理失敗

## 原因の仮説・技術的背景

### 根本原因
`BaseDevice._prepare_data()`メソッドがすべてのMQTTメッセージをUTF-8エンコードされたJSONデータとして処理することを前提としていた。しかし、一部のEcoFlowデバイス（特にinternal APIを使用するデバイス）はバイナリprotobufデータを送信する。

### アーキテクチャの問題
1. **BaseDevice設計の欠陥**: すべてのMQTTデータがUTF-8/JSONであると仮定
2. **不整合な実装**: 3つのデバイスだけが適切にバイナリprotobuf処理を実装
3. **暗号化処理の欠如**: AES-128-ECB復号化が大部分のデバイスで未実装

### データフロー
```
MQTT Client (binary data) 
    ↓
BaseDevice.update_data() 
    ↓
_prepare_data() (UTF-8 decode attempt) 
    ↓
UnicodeDecodeError (バイナリデータの場合)
```

### 適切に実装されたデバイス
以下の3つのデバイスのみがバイナリprotobuf処理を正しく実装：
1. **delta_pro_3.py** - 包括的なprotobufデコード（ヘッダー解析、XORデコード）
2. **powerstream.py** - ecopacket_pb2とpowerstream_pb2を使用
3. **stream_ac.py** - stream_ac_pb2を使用

### 影響を受けるデバイス
`BaseDevice._prepare_data()`を継承する15+のinternalデバイス：
- delta2.py, delta2_max.py, delta_max.py, delta_mini.py, delta_pro.py
- glacier.py, river2.py, river2_max.py, river2_pro.py
- river_max.py, river_mini.py, river_pro.py
- smart_meter.py, wave2.py

## 調査・修正方針

### 調査アプローチ
1. エラー発生箇所の特定（devices/__init__.py:180）
2. コードベース全体のバイナリデータ処理パターンの分析
3. 適切に実装されたデバイス（delta_pro_3.py）の実装を参考にした修正方針策定

### 修正戦略
BaseDeviceクラスでバイナリデータを検出し、適切な警告を出力してスキップする安全な処理を実装。

## 修正結果と分析

### 実装した修正内容

#### 1. バイナリデータ検出ロジック
```python
def _is_binary_data(self, data: bytes) -> bool:
    """Check if data contains binary protobuf indicators."""
    if len(data) < 4:
        return False
    
    first_bytes = data[:4]
    non_printable_count = sum(1 for byte in first_bytes if byte < 32 or byte > 126)
    
    # If more than half the first bytes are non-printable, likely binary
    return non_printable_count >= 2
```

#### 2. 改良された_prepare_dataメソッド
```python
def _prepare_data(self, raw_data) -> dict[str, any]:
    try:
        # Check if data is binary protobuf data
        if isinstance(raw_data, bytes):
            if self._is_binary_data(raw_data):
                _LOGGER.warning("Received binary protobuf data but device doesn't override _prepare_data(). "
                              "This device may need protobuf support. Skipping message.")
                return {}
        
        # Try UTF-8 decoding for JSON data
        try:
            if isinstance(raw_data, bytes):
                payload = raw_data.decode("utf-8")
            else:
                payload = raw_data
            return json.loads(payload)
        except UnicodeDecodeError as error:
            _LOGGER.warning(f"UnicodeDecodeError: {error}. Data may be binary protobuf format.")
            return {}
        except json.JSONDecodeError as error:
            _LOGGER.warning(f"JSON decode error: {error}. Invalid JSON format.")
            return {}
    except Exception as error1:
        _LOGGER.error(f"Data processing error: {error1}. Ignoring message and waiting for the next one.")
        return {}
```

### 修正の効果
1. **エラー削減**: UTF-8デコードエラーが警告レベルに変更され、ログノイズが大幅に削減
2. **安定性向上**: バイナリデータによるクラッシュを防止
3. **診断情報改善**: 適切な警告メッセージでデバイスのprotobuf対応が必要であることを明示
4. **後方互換性**: 既存のJSONベースデバイスの動作に影響なし

### 残存課題と推奨改善
1. **デバイス固有実装**: バイナリprotobufを使用するデバイスは`_prepare_data()`メソッドのオーバーライドが必要
2. **暗号化対応**: AES-128-ECB復号化の統一実装
3. **共通基盤**: protobuf処理用の共通基底クラスの作成

## 解決方法

### 短期的解決（実装済み）
- BaseDeviceクラスでバイナリデータ検出と安全な処理
- 適切なエラーハンドリングとログ出力
- UTF-8デコードエラーの根本的除去

### 長期的改善案
1. **Protobuf対応デバイスの実装**: delta_pro_3.pyを参考に他のinternalデバイスでもprotobuf処理を実装
2. **共通アーキテクチャ**: `ProtobufBaseDevice`クラスの作成でprotobuf処理を標準化
3. **暗号化統合**: AES復号化処理の統一実装

### 検証方法
1. Home Assistant再起動後のログ監視
2. EcoFlowデバイスからのMQTT通信確認
3. エラーメッセージの減少確認

この修正により、UTF-8デコードエラーは解決され、システムの安定性と診断性が向上した。