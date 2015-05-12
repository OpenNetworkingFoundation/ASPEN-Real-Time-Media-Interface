/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */
package org.tmf.dsmapi.inventory.resource.model;

import java.io.Serializable;
import javax.persistence.Embeddable;

/**
 *
 * @author John Morey <jmorey@mmintl.com>
 */

@Embeddable
public class FlowElement implements Serializable {
        private String ipAddressType;
        private String sourceIpAddress;
        private String sourceIpPort;
        private String destinationIpAddress;
        private String destinationIpPort;
        private String transportType;
        private String flowId;

    /**
     * @return the ipAddressType
     */
    public String getIpAddressType() {
        return ipAddressType;
    }

    /**
     * @param ipAddressType the ipAddressType to set
     */
    public void setIpAddressType(String ipAddressType) {
        this.ipAddressType = ipAddressType;
    }

    /**
     * @return the sourceIpAddress
     */
    public String getSourceIpAddress() {
        return sourceIpAddress;
    }

    /**
     * @param sourceIpAddress the sourceIpAddress to set
     */
    public void setSourceIpAddress(String sourceIpAddress) {
        this.sourceIpAddress = sourceIpAddress;
    }

    /**
     * @return the sourceIpPort
     */
    public String getSourceIpPort() {
        return sourceIpPort;
    }

    /**
     * @param sourceIpPort the sourceIpPort to set
     */
    public void setSourceIpPort(String sourceIpPort) {
        this.sourceIpPort = sourceIpPort;
    }

    /**
     * @return the destinationIpAddress
     */
    public String getDestinationIpAddress() {
        return destinationIpAddress;
    }

    /**
     * @param destinationIpAddress the destinationIpAddress to set
     */
    public void setDestinationIpAddress(String destinationIpAddress) {
        this.destinationIpAddress = destinationIpAddress;
    }

    /**
     * @return the destinationIpPort
     */
    public String getDestinationIpPort() {
        return destinationIpPort;
    }

    /**
     * @param destinationIpPort the destinationIpPort to set
     */
    public void setDestinationIpPort(String destinationIpPort) {
        this.destinationIpPort = destinationIpPort;
    }

    /**
     * @return the transportType
     */
    public String getTransportType() {
        return transportType;
    }

    /**
     * @param transportType the transportType to set
     */
    public void setTransportType(String transportType) {
        this.transportType = transportType;
    }

    /**
     * @return the flowId
     */
    public String getFlowId() {
        return flowId;
    }

    /**
     * @param flowId the flowId to set
     */
    public void setFlowId(String flowId) {
        this.flowId = flowId;
    }
}
