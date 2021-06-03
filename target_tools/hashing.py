# Copyright 2021 Adobe. All rights reserved.
# This file is licensed to you under the Apache License, Version 2.0 (the "License")
# you may not use this file except in compliance with the License. You may obtain a copy
# of the License at http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR REPRESENTATIONS
# OF ANY KIND, either express or implied. See the License for the specific language
# governing permissions and limitations under the License.
"""Hashing functions"""
# pylint: disable=invalid-name
import ctypes
from target_tools.utils import memoize


def zero_fill_right_shift(val, n):
    """bitwise >>>"""
    return (val >> n) if val >= 0 else ((val + 0x100000000) >> n)


def char_code_at(string_value, index):
    """Gets unicode value of character at given index of string_value"""
    return ord(string_value[index])


def int32(val):
    """Convert standard python int value into a 32-bit signed int"""
    return ctypes.c_int(val).value


def mul32(m, n):
    """mul32"""
    nlo = n & 0xffff
    nhi = n - nlo
    return int32(int32(int32(nhi * m ^ 0) | 0) + int32(int32(nlo * m) | 0)) | 0


def hash_unencoded_chars_raw(string_value, seed=0):
    """Optimized MurmurHash3 (32-bit) hashing algorithm to generate a signed numeric 10-digit hash
    This method matches the java method used on Target Edge
    :param string_value: (str) string to hash
    :param seed: (int) seed value
    :return: (int) Returns 10-digit signed int hash value
    """
    length = len(string_value)
    c1 = 0xcc9e2d51
    c2 = 0x1b873593

    h1 = seed
    rounded_end = length & ~0x1

    for i in range(0, rounded_end, 2):
        k1 = char_code_at(string_value, i) | (char_code_at(string_value, i + 1) << 16)

        k1 = mul32(k1, c1)
        k1 = (int32((k1 & 0x1ffff) << 15)) | int32(zero_fill_right_shift(k1, 17))  # ROTL32(k1,15)
        k1 = mul32(k1, c2)

        h1 ^= k1
        h1 = int32(int32(h1 & 0x7ffff) << 13) | int32(zero_fill_right_shift(h1, 19))  # ROTL32(h1,13)
        h1 = int32(h1 * 5 + 0xe6546b64) | 0

    if length % 2 == 1:
        k1 = char_code_at(string_value, rounded_end)
        k1 = mul32(k1, c1)
        k1 = int32(int32(k1 & 0x1ffff) << 15) | int32(zero_fill_right_shift(k1, 17))  # ROTL32(k1,15)
        k1 = mul32(k1, c2)
        h1 ^= k1

    # finalization
    h1 ^= length << 1

    # fmix(h1)
    h1 ^= int32(zero_fill_right_shift(h1, 16))
    h1 = mul32(h1, 0x85ebca6b)
    h1 ^= int32(zero_fill_right_shift(h1, 13))
    h1 = mul32(h1, 0xc2b2ae35)
    h1 ^= int32(zero_fill_right_shift(h1, 16))

    return h1


def _create_memoization_key(args, kwargs):
    """Joins list of values to create memo cache key"""
    return "-".join(args)


hash_unencoded_chars = memoize(hash_unencoded_chars_raw, _create_memoization_key)
