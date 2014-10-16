/*
 * DEBUG: section 00    Client Database
 * AUTHOR: Duane Wessels
 *
 * SQUID Web Proxy Cache          http://www.squid-cache.org/
 * ----------------------------------------------------------
 *
 *  Squid is the result of efforts by numerous individuals from
 *  the Internet community; see the CONTRIBUTORS file for full
 *  details.   Many organizations have provided support for Squid's
 *  development; see the SPONSORS file for full details.  Squid is
 *  Copyrighted (C) 2001 by the Regents of the University of
 *  California; see the COPYRIGHT file for full details.  Squid
 *  incorporates software developed and/or copyrighted by other
 *  sources; see the CREDITS file for full details.
 *
 *  This program is free software; you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation; either version 2 of the License, or
 *  (at your option) any later version.
 *
 *  This program is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License
 *  along with this program; if not, write to the Free Software
 *  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111, USA.
 *
 */

#ifndef SQUID_CLIENT_DB_H_
#define SQUID_CLIENT_DB_H_

#include "anyp/ProtocolType.h"
//#include "enums.h"
#include "ip/Address.h"
#include "LogTags.h"

namespace Ip
{
class Address;
}

class StoreEntry;
class ClientInfo;

void clientdbUpdate(const Ip::Address &, LogTags, AnyP::ProtocolType, size_t);
int clientdbCutoffDenied(const Ip::Address &);
void clientdbDump(StoreEntry *);
void clientdbFreeMemory(void);
int clientdbEstablished(const Ip::Address &, int);

#if USE_DELAY_POOLS
void clientdbSetWriteLimiter(ClientInfo * info, const int writeSpeedLimit,const double initialBurst,const double highWatermark);
ClientInfo * clientdbGetInfo(const Ip::Address &addr);
#endif

#if SQUID_SNMP
Ip::Address *client_entry(Ip::Address *current);
#endif

#endif /* SQUID_CLIENT_DB_H_ */