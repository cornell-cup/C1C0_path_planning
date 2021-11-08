#ifndef R2_PROTOCOL_H
#define R2_PROTOCOL_H

#include <stdint.h>
#include <string.h>

#define R2P_HEADER_SIZE 16

static const uint16_t r2p_crc16_table[256] = {
  0x0000, 0x1021, 0x2042, 0x3063, 0x4084, 0x50a5, 0x60c6, 0x70e7,
  0x8108, 0x9129, 0xa14a, 0xb16b, 0xc18c, 0xd1ad, 0xe1ce, 0xf1ef,
  0x1231, 0x0210, 0x3273, 0x2252, 0x52b5, 0x4294, 0x72f7, 0x62d6,
  0x9339, 0x8318, 0xb37b, 0xa35a, 0xd3bd, 0xc39c, 0xf3ff, 0xe3de,
  0x2462, 0x3443, 0x0420, 0x1401, 0x64e6, 0x74c7, 0x44a4, 0x5485,
  0xa56a, 0xb54b, 0x8528, 0x9509, 0xe5ee, 0xf5cf, 0xc5ac, 0xd58d,
  0x3653, 0x2672, 0x1611, 0x0630, 0x76d7, 0x66f6, 0x5695, 0x46b4,
  0xb75b, 0xa77a, 0x9719, 0x8738, 0xf7df, 0xe7fe, 0xd79d, 0xc7bc,
  0x48c4, 0x58e5, 0x6886, 0x78a7, 0x0840, 0x1861, 0x2802, 0x3823,
  0xc9cc, 0xd9ed, 0xe98e, 0xf9af, 0x8948, 0x9969, 0xa90a, 0xb92b,
  0x5af5, 0x4ad4, 0x7ab7, 0x6a96, 0x1a71, 0x0a50, 0x3a33, 0x2a12,
  0xdbfd, 0xcbdc, 0xfbbf, 0xeb9e, 0x9b79, 0x8b58, 0xbb3b, 0xab1a,
  0x6ca6, 0x7c87, 0x4ce4, 0x5cc5, 0x2c22, 0x3c03, 0x0c60, 0x1c41,
  0xedae, 0xfd8f, 0xcdec, 0xddcd, 0xad2a, 0xbd0b, 0x8d68, 0x9d49,
  0x7e97, 0x6eb6, 0x5ed5, 0x4ef4, 0x3e13, 0x2e32, 0x1e51, 0x0e70,
  0xff9f, 0xefbe, 0xdfdd, 0xcffc, 0xbf1b, 0xaf3a, 0x9f59, 0x8f78,
  0x9188, 0x81a9, 0xb1ca, 0xa1eb, 0xd10c, 0xc12d, 0xf14e, 0xe16f,
  0x1080, 0x00a1, 0x30c2, 0x20e3, 0x5004, 0x4025, 0x7046, 0x6067,
  0x83b9, 0x9398, 0xa3fb, 0xb3da, 0xc33d, 0xd31c, 0xe37f, 0xf35e,
  0x02b1, 0x1290, 0x22f3, 0x32d2, 0x4235, 0x5214, 0x6277, 0x7256,
  0xb5ea, 0xa5cb, 0x95a8, 0x8589, 0xf56e, 0xe54f, 0xd52c, 0xc50d,
  0x34e2, 0x24c3, 0x14a0, 0x0481, 0x7466, 0x6447, 0x5424, 0x4405,
  0xa7db, 0xb7fa, 0x8799, 0x97b8, 0xe75f, 0xf77e, 0xc71d, 0xd73c,
  0x26d3, 0x36f2, 0x0691, 0x16b0, 0x6657, 0x7676, 0x4615, 0x5634,
  0xd94c, 0xc96d, 0xf90e, 0xe92f, 0x99c8, 0x89e9, 0xb98a, 0xa9ab,
  0x5844, 0x4865, 0x7806, 0x6827, 0x18c0, 0x08e1, 0x3882, 0x28a3,
  0xcb7d, 0xdb5c, 0xeb3f, 0xfb1e, 0x8bf9, 0x9bd8, 0xabbb, 0xbb9a,
  0x4a75, 0x5a54, 0x6a37, 0x7a16, 0x0af1, 0x1ad0, 0x2ab3, 0x3a92,
  0xfd2e, 0xed0f, 0xdd6c, 0xcd4d, 0xbdaa, 0xad8b, 0x9de8, 0x8dc9,
  0x7c26, 0x6c07, 0x5c64, 0x4c45, 0x3ca2, 0x2c83, 0x1ce0, 0x0cc1,
  0xef1f, 0xff3e, 0xcf5d, 0xdf7c, 0xaf9b, 0xbfba, 0x8fd9, 0x9ff8,
  0x6e17, 0x7e36, 0x4e55, 0x5e74, 0x2e93, 0x3eb2, 0x0ed1, 0x1ef0
};

/**
 * Compute the CRC16 CCITT checksum of data.
 *
 * @param   data  Unsigned 8 bit array of data
 * @param   len   Length of the data array
 * @return  The CRC as an unsigned 16 bit integer
 */
inline uint16_t r2p_crc16(const uint8_t* data, uint32_t len) {
  uint16_t crc = 0xffff;
  while (len-- > 0) {
    crc = (crc << 8) ^ r2p_crc16_table[((crc >> 8) ^ *data++) & 0xff];
  }

  // Avoid a CRC of 0
  if (crc == 0) {
    crc++;
  }
  return crc;
}

/**
 * Encode data into a preallocated buffer (length of data + 16) with no checksum.
 *
 * @param   type  4 char type of the packet
 * @param   data  Unsigned 8 bit array of data
 * @param   data_len  Length of data array
 * @param   buffer  Pointer to preallocated output buffer
 * @param   buffer_len  Length of preallocated buffer
 * @return  Number of bytes written, -1 if failed
 */
inline int32_t r2p_encode_nocs(const char type[5], const uint8_t* data, uint32_t data_len, uint8_t* buffer, uint32_t buffer_len) {
  // Make sure the buffer is large enough
  if (buffer_len < data_len + R2P_HEADER_SIZE) {
    return -1;
  }

  // Starting sequence
  buffer[0] = 0xa2;
  buffer[1] = 0xb2;
  buffer[2] = 0xc2;

  // Checksum
  buffer[3] = 0x00;
  buffer[4] = 0x00;

  // Type
  memcpy(buffer + 5, type, 4);

  // Length of data (big endian)
  buffer[9] = (data_len >> 24) & 0xff;
  buffer[10] = (data_len >> 16) & 0xff;
  buffer[11] = (data_len >> 8) & 0xff;
  buffer[12] = data_len & 0xff;

  // Data
  memcpy(buffer + 13, data, data_len);

  // Ending sequence
  buffer[data_len + 13] = 0xd2;
  buffer[data_len + 14] = 0xe2;
  buffer[data_len + 15] = 0xf2;

  return data_len + R2P_HEADER_SIZE;
}

/**
 * Encode data into a preallocated buffer (length of data + 16).
 *
 * @param   type  4 char type of the packet
 * @param   data  Unsigned 8 bit array of data
 * @param   data_len  Length of data array
 * @param   buffer  Pointer to preallocated output buffer
 * @param   buffer_len  Length of preallocated buffer
 * @return  Number of bytes written, -1 if failed
 */
inline int32_t r2p_encode(const char type[5], const uint8_t* data, uint32_t data_len, uint8_t* buffer, uint32_t buffer_len) {
  // Encode without the checksum first
  uint32_t n = r2p_encode_nocs(type, data, data_len, buffer, buffer_len);
  if (n < 0) {
    return -1;
  }
  // Compute the checksum and add to the buffer
  uint16_t crc = r2p_crc16(data, data_len);
  buffer[3] = (crc >> 8) & 0xff;
  buffer[4] = crc & 0xff;
  return n;
}

/**
 * Decode data into preallocated buffers, skipping the checksum.
 *
 * @param   buffer  Unsigned 8 bit array of encoded data
 * @param   buffer_len  Length of encoded data array
 * @param   type  Output 4 char type of data
 * @param   checksum  Output 16 bit checksum
 * @param   data  Output unsigned 8 bit array of data
 * @param   data_len  Output length of output data array
 * @return  Number of bytes read, -1 if failed to parse
 */
inline int32_t r2p_decode_nocs(const uint8_t* buffer, uint32_t buffer_len, uint16_t* checksum, char type[5], uint8_t* data, uint32_t* data_len) {
  // Search for the starting byte
  uint32_t index = 0;
  while (index < buffer_len - 2 && !(buffer[index] == 0xa2 &&
      buffer[index + 1] == 0xb2 && buffer[index + 2] == 0xc2)) index++;
  if (index >= buffer_len - 2) { // Failed to find the starting sequence
    return -1;
  }

  // Make sure there is enough in the buffer for the header
  if (buffer_len - index < R2P_HEADER_SIZE) {
    return -1;
  }

  // Checksum
  *checksum = (buffer[index + 3] << 8) | buffer[index + 4];

  // Type
  memcpy(type, buffer + 5, 4);

  // Length of data (big endian)
  *data_len = (buffer[index + 9] << 24) | (buffer[index + 10] << 16) | (buffer[index + 11] << 8) | buffer[index + 12];

  // Data
  memcpy(data, buffer + index + 13, *data_len);

  // Ending sequence
  if (buffer[index + *data_len + 13] == 0xd2 && buffer[index + *data_len + 14] == 0xe2 && buffer[index + *data_len + 15] == 0xf2) {
    return index + *data_len + R2P_HEADER_SIZE;
  }
  return -1;
}

/**
 * Decode data into preallocated buffers.
 *
 * @param   buffer  Unsigned 8 bit array of encoded data
 * @param   buffer_len  Length of encoded data array
 * @param   type  Output 4 char type of data
 * @param   checksum  Output 16 bit checksum
 * @param   data  Output unsigned 8 bit array of data
 * @param   data_len  Output length of output data array
 * @return  Number of bytes read, -1 if failed to parse, -2 if failed checksum
 */
inline int32_t r2p_decode(const uint8_t* buffer, uint32_t buffer_len, uint16_t* checksum, char type[5], uint8_t* data, uint32_t* data_len) {
  // Decode without checking the checksum first
  uint32_t n = r2p_decode_nocs(buffer, buffer_len, checksum, type, data, data_len);
  if (n < 0) {
    return -1;
  }

  // A checksum of 0 signifies no checksum
  if (*checksum == 0) {
    return n;
  }

  // Compute the checksum and compare
  uint16_t crc = r2p_crc16(data, *data_len);
  if (crc == *checksum) {
    return n;
  }
  return -2;
}

// FSM States
#define R2PF_STATE_START 0
#define R2PF_STATE_CHECKSUM 10
#define R2PF_STATE_TYPE 20
#define R2PF_STATE_LENGTH 30
#define R2PF_STATE_DATA 40
#define R2PF_STATE_END 50
#define R2PF_STATE_DONE 60

typedef struct {
  int16_t state;
  uint8_t* buffer;
  uint32_t buffer_len;
  uint32_t buffer_index;
  uint16_t crc;

  uint16_t checksum;
  char type[4];
  uint8_t* data;
  uint32_t data_len;

  uint8_t done;
} r2pf_t;

inline r2pf_t r2pf_init(uint8_t* buffer, uint32_t buffer_len) {
  // TODO Check buffer length
  return (r2pf_t) { R2PF_STATE_START, buffer, buffer_len, 0, 0xffff };
}

inline void r2pf_read(r2pf_t* fsm, uint8_t read) {
  uint8_t* buffer = fsm->buffer;
  switch (fsm->state) {
    default:
    case R2PF_STATE_START:
      if ((fsm->buffer_index == 0 && read == 0xa2)
          || (fsm->buffer_index == 1 && read == 0xb2)
          || (fsm->buffer_index == 2 && read == 0xc2)) {
        buffer[fsm->buffer_index] = read;
        fsm->buffer_index++;
        if (fsm->buffer_index == 3) {
          fsm->state = R2PF_STATE_CHECKSUM;
          fsm->done = 0;
          fsm->crc = 0xffff;
        }
      }
      else {
        fsm->buffer_index = 0;
      }
      break;
    case R2PF_STATE_CHECKSUM:
      buffer[fsm->buffer_index] = read;
      fsm->buffer_index++;
      if (fsm->buffer_index == 5) {
        fsm->checksum = (buffer[3] << 8) | buffer[4];
        fsm->state = R2PF_STATE_TYPE;
      }
      break;
    case R2PF_STATE_TYPE:
      buffer[fsm->buffer_index] = read;
      fsm->buffer_index++;
      if (fsm->buffer_index == 9) {
        memcpy(fsm->type, buffer + 5, 4);
        fsm->state = R2PF_STATE_LENGTH;
      }
      break;
    case R2PF_STATE_LENGTH:
      buffer[fsm->buffer_index] = read;
      fsm->buffer_index++;
      if (fsm->buffer_index == 13) {
        fsm->data_len = (buffer[9] << 24) | (buffer[10] << 16) | (buffer[11] << 8) | buffer[12];
        if (fsm->data_len > 0) {
          fsm->state = R2PF_STATE_DATA;
        }
        else {
          fsm->state = R2PF_STATE_END;
        }
      }
      break;
    case R2PF_STATE_DATA:
      buffer[fsm->buffer_index] = read;
      if (fsm->crc != 0) {
        fsm->crc = (fsm->crc << 8) ^ r2p_crc16_table[((fsm->crc >> 8) ^ read) & 0xff];
      }
      fsm->buffer_index++;
      if (fsm->buffer_index == 13 + fsm->data_len) {
        fsm->data = buffer + 13;
        fsm->state = R2PF_STATE_END;

        // Avoid a crc of 0
        if (fsm->crc == 0) {
          fsm->crc++;
        }
      }
      break;
    case R2PF_STATE_END:
      if ((fsm->buffer_index == fsm->data_len + 13 && read == 0xd2)
          || (fsm->buffer_index == fsm->data_len + 14 && read == 0xe2)
          || (fsm->buffer_index == fsm->data_len + 15 && read == 0xf2)) {
        buffer[fsm->buffer_index] = read;
        fsm->buffer_index++;
        if (fsm->buffer_index == fsm->data_len + 16) {
          // TODO Check CRC
          fsm->state = R2PF_STATE_START;
          fsm->buffer_index = 0;
          fsm->done = 1;
        }
      }
      else {
        fsm->state = R2PF_STATE_START;
        fsm->buffer_index = 0;
        fsm->done = 0;
      }
      break;
  }
}

#endif
