/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */
package org.tmf.dsmapi.inventory.resource.model;

import javax.persistence.Embeddable;

/**
 *
 * @author John Morey <jmorey@mmintl.com>
 */

@Embeddable
public class FlowSpecElement {
    private String ipAddressType;
    private String transport;
    private String sourceIPAddressRange;
    private String sourceIPPortRange;
    private String destinationIPAddressRange;
    private String destinationIPPortRange;

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
     * @return the transport
     */
    public String getTransport() {
        return transport;
    }

    /**
     * @param transport the transport to set
     */
    public void setTransport(String transport) {
        this.transport = transport;
    }

    /**
     * @return the sourceIPAddressRange
     */
    public String getSourceIPAddressRange() {
        return sourceIPAddressRange;
    }

    /**
     * @param sourceIPAddressRange the sourceIPAddressRange to set
     */
    public void setSourceIPAddressRange(String sourceIPAddressRange) {
        this.sourceIPAddressRange = sourceIPAddressRange;
    }

    /**
     * @return the sourceIPPortRange
     */
    public String getSourceIPPortRange() {
        return sourceIPPortRange;
    }

    /**
     * @param sourceIPPortRange the sourceIPPortRange to set
     */
    public void setSourceIPPortRange(String sourceIPPortRange) {
        this.sourceIPPortRange = sourceIPPortRange;
    }

    /**
     * @return the destinationIPAddressRange
     */
    public String getDestinationIPAddressRange() {
        return destinationIPAddressRange;
    }

    /**
     * @param destinationIPAddressRange the destinationIPAddressRange to set
     */
    public void setDestinationIPAddressRange(String destinationIPAddressRange) {
        this.destinationIPAddressRange = destinationIPAddressRange;
    }

    /**
     * @return the destinationIPPortRange
     */
    public String getDestinationIPPortRange() {
        return destinationIPPortRange;
    }

    /**
     * @param destinationIPPortRange the destinationIPPortRange to set
     */
    public void setDestinationIPPortRange(String destinationIPPortRange) {
        this.destinationIPPortRange = destinationIPPortRange;
    }
}
