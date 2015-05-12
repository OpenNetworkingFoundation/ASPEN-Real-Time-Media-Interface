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
public class GrantedQoS implements Serializable {
    private String actualClass;
    private long dscp;
    private String actualBandwidth;

    /**
     * @return the actualClass
     */
    public String getActualClass() {
        return actualClass;
    }

    /**
     * @param actualClass the actualClass to set
     */
    public void setActualClass(String actualClass) {
        this.actualClass = actualClass;
    }

    /**
     * @return the dscp
     */
    public long getDscp() {
        return dscp;
    }

    /**
     * @param dscp the dscp to set
     */
    public void setDscp(long dscp) {
        this.dscp = dscp;
    }

    /**
     * @return the actualBandwidth
     */
    public String getActualBandwidth() {
        return actualBandwidth;
    }

    /**
     * @param actualBandwidth the actualBandwidth to set
     */
    public void setActualBandwidth(String actualBandwidth) {
        this.actualBandwidth = actualBandwidth;
    }
}
