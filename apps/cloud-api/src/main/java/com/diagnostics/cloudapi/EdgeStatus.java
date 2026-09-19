package com.diagnostics.cloudapi;

import java.time.Instant;

/** 云端接收的边端状态。 */
public record EdgeStatus(String edgeId, String site, Instant reportedAt, Instant receivedAt) {}
