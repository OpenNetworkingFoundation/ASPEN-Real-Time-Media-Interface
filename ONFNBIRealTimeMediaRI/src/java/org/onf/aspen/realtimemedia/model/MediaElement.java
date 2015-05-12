/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */
package org.onf.aspen.realtimemedia.model;

import javax.persistence.Embeddable;

/**
 *
 * @author John Morey <jmorey@mmintl.com>
 */

@Embeddable
public class MediaElement {
    private FlowElement flowElement;
    private GrantedQoS grantedQoS;
    private RequestedQoS requestedQoS;
    private Integer ageOutTimer;

    /**
     * @return the flowElement
     */
    public FlowElement getFlowElement() {
        return flowElement;
    }

    /**
     * @param flowElement the flowElement to set
     */
    public void setFlowElement(FlowElement flowElement) {
        this.flowElement = flowElement;
    }

    /**
     * @return the grantedQoS
     */
    public GrantedQoS getGrantedQoS() {
        return grantedQoS;
    }

    /**
     * @param grantedQoS the grantedQoS to set
     */
    public void setGrantedQoS(GrantedQoS grantedQoS) {
        this.grantedQoS = grantedQoS;
    }

    /**
     * @return the requestedQoS
     */
    public RequestedQoS getRequestedQoS() {
        return requestedQoS;
    }

    /**
     * @param requestedQoS the requestedQoS to set
     */
    public void setRequestedQoS(RequestedQoS requestedQoS) {
        this.requestedQoS = requestedQoS;
    }

    /**
     * @return the ageOutTimer
     */
    public Integer getAgeOutTimer() {
        return ageOutTimer;
    }

    /**
     * @param ageOutTimer the ageOutTimer to set
     */
    public void setAgeOutTimer(Integer ageOutTimer) {
        this.ageOutTimer = ageOutTimer;
    }
}
