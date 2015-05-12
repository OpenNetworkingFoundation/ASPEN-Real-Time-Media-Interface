/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */
package org.onf.aspen.realtimemedia.model;

import java.io.Serializable;
import javax.persistence.Embeddable;

/**
 *
 * @author John Morey <jmorey@mmintl.com>
 */

@Embeddable
public class RequestedQoS implements Serializable {
        private String applicationClass;
        private Long averageBandwidth;
        private Long maxBandwidth;
        private Long minBandwidth;

    /**
     * @return the applicationClass
     */
    public String getApplicationClass() {
        return applicationClass;
    }

    /**
     * @param applicationClass the applicationClass to set
     */
    public void setApplicationClass(String applicationClass) {
        this.applicationClass = applicationClass;
    }

    /**
     * @return the averageBandwidth
     */
    public Long getAverageBandwidth() {
        return averageBandwidth;
    }

    /**
     * @param averageBandwidth the averageBandwidth to set
     */
    public void setAverageBandwidth(Long averageBandwidth) {
        this.averageBandwidth = averageBandwidth;
    }

    /**
     * @return the maxBandwidth
     */
    public Long getMaxBandwidth() {
        return maxBandwidth;
    }

    /**
     * @param maxBandwidth the maxBandwidth to set
     */
    public void setMaxBandwidth(Long maxBandwidth) {
        this.maxBandwidth = maxBandwidth;
    }

    /**
     * @return the minBandwidth
     */
    public Long getMinBandwidth() {
        return minBandwidth;
    }

    /**
     * @param minBandwidth the minBandwidth to set
     */
    public void setMinBandwidth(Long minBandwidth) {
        this.minBandwidth = minBandwidth;
    }
    
}
